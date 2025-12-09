# Core/methodology_validator.py

import re
from statistics import mean
from typing import Dict, List


class MethodologyValidator:
    """
    Heuristic, transparent methodology analyzer.

    It looks for:
      - study design terminology (randomized, blinded, observational, etc.)
      - sample size reporting (n = 120)
      - control / comparison groups and blinding
      - transparency signals (preregistration, data sharing)

    Returns a structured summary and an overall methodology score in [0, 1].
    """

    def analyze(self, text: str) -> Dict:
        lowered = text.lower()

        design_hits = self._find_design_terms(lowered)
        sample_info = self._extract_sample_sizes(lowered)
        control_info = self._find_control_and_blinding(lowered)
        transparency_info = self._find_transparency_signals(lowered)

        # ---- Scoring heuristics ----

        # Design score: more explicit design terms → higher score
        design_components = 0
        if design_hits["has_experimental"]:
            design_components += 1
        if design_hits["has_observational"]:
            design_components += 1
        if design_hits["has_randomization"]:
            design_components += 1
        if design_hits["has_longitudinal_or_cross_sectional"]:
            design_components += 1
        design_score = design_components / 4.0  # 0–1

        # Sample score: more/larger sample sizes → better
        n_values = sample_info["values"]
        if n_values:
            avg_n = mean(n_values)
            # 0 at n <= 10, 1 at n >= 200 (clamped)
            sample_score = max(0.0, min((avg_n - 10) / (200 - 10), 1.0))
        else:
            sample_score = 0.0

        # Control / blinding score
        control_score = 0.0
        if control_info["has_control_group"]:
            control_score += 0.4
        if control_info["has_placebo_or_comparison"]:
            control_score += 0.3
        if control_info["has_blinding"]:
            control_score += 0.3

        # Transparency score
        transparency_score = 0.0
        if transparency_info["has_preregistration"]:
            transparency_score += 0.4
        if transparency_info["has_data_sharing"]:
            transparency_score += 0.3
        if transparency_info["has_protocol_or_repository"]:
            transparency_score += 0.3

        # Weighted overall methodology score
        overall_score = (
            0.30 * design_score
            + 0.25 * sample_score
            + 0.25 * (control_score)
            + 0.20 * (transparency_score)
        )
        overall_score = min(overall_score, 1.0)

        # Small-sample warning
        small_sample_warning = bool(n_values and max(n_values) < 30)

        return {
            "design": design_hits,
            "sample_size": {
                "count": len(n_values),
                "values": n_values,
                "small_sample_warning": small_sample_warning,
            },
            "control_and_blinding": control_info,
            "transparency": transparency_info,
            "overall_methodology_score": overall_score,
        }

    # --------- Internal helpers ---------

    def _find_design_terms(self, lowered: str) -> Dict:
        experimental_terms = [
            "experiment", "experimental", "intervention",
            "manipulated", "treatment group",
        ]
        observational_terms = [
            "observational", "survey", "case study",
            "cohort study", "case-control", "ecological study",
        ]
        randomization_terms = [
            "randomized", "randomised", "randomization", "randomisation",
            "randomly assigned",
        ]
        long_cross_terms = [
            "longitudinal", "cross-sectional", "cross sectional",
            "time series", "follow-up", "follow up",
        ]

        def any_in(terms: List[str]) -> bool:
            return any(t in lowered for t in terms)

        return {
            "has_experimental": any_in(experimental_terms),
            "has_observational": any_in(observational_terms),
            "has_randomization": any_in(randomization_terms),
            "has_longitudinal_or_cross_sectional": any_in(long_cross_terms),
            "design_terms_found": [
                t for t in experimental_terms + observational_terms
                + randomization_terms + long_cross_terms
                if t in lowered
            ],
        }

    def _extract_sample_sizes(self, lowered: str) -> Dict:
        """
        Looks for 'n = 120', 'N=35', etc. and returns list of ints.
        """
        pattern = re.compile(r"\b[nsn]\s*=\s*(\d{1,5})", re.IGNORECASE)
        matches = pattern.findall(lowered)
        values: List[int] = []
        for m in matches:
            try:
                values.append(int(m))
            except ValueError:
                continue
        return {
            "values": values,
        }

    def _find_control_and_blinding(self, lowered: str) -> Dict:
        control_group_terms = [
            "control group", "control condition", "comparison group",
            "baseline group", "reference group",
        ]
        placebo_terms = [
            "placebo", "sham", "dummy treatment",
        ]
        blinding_terms = [
            "double-blind", "double blind", "single-blind", "single blind",
            "triple-blind", "blinded", "masked", "observer-blind",
        ]

        def any_in(terms: List[str]) -> bool:
            return any(t in lowered for t in terms)

        return {
            "has_control_group": any_in(control_group_terms),
            "has_placebo_or_comparison": any_in(placebo_terms),
            "has_blinding": any_in(blinding_terms),
            "examples": [
                t for t in control_group_terms + placebo_terms + blinding_terms
                if t in lowered
            ],
        }

    def _find_transparency_signals(self, lowered: str) -> Dict:
        prereg_terms = [
            "preregistered", "pre-registered", "registered report",
            "clinicaltrials.gov", "trial registration", "osf.io",
        ]
        data_sharing_terms = [
            "data are available", "data is available",
            "data available upon request", "open data",
            "data repository", "zenodo", "figshare", "dryad",
        ]
        protocol_terms = [
            "protocol", "analysis plan", "study protocol",
            "supplementary methods", "supplementary material",
        ]

        def any_in(terms: List[str]) -> bool:
            return any(t in lowered for t in terms)

        return {
            "has_preregistration": any_in(prereg_terms),
            "has_data_sharing": any_in(data_sharing_terms),
            "has_protocol_or_repository": any_in(protocol_terms),
            "examples": [
                t for t in prereg_terms + data_sharing_terms + protocol_terms
                if t in lowered
            ],
        }
