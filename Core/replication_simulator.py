# Core/replication_simulator.py

from __future__ import annotations

from typing import Dict, Any, Optional


class ReplicationSimulator:
    """
    Simple rule-based replication / robustness signal extractor (Option A schema).

    Emits:
      - overall_replicability_score: float in [0, 1]
      - simulated_replication_outcome: "likely_replicable" | "uncertain" | "fragile"
      - claims
      - robustness
      - openness
      - upstream_signals

    Also includes legacy alias:
      - overall_replication_score
    """

    def analyze_replication(
        self,
        text: str,
        stats: Optional[Dict[str, Any]] = None,
        methodology: Optional[Dict[str, Any]] = None,
        citations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        stats = stats or {}
        methodology = methodology or {}
        citations = citations or {}

        lowered = (text or "").lower().strip()

        # ---- Empty text defaults ----
        if not lowered:
            return {
                "overall_replicability_score": 0.0,
                "simulated_replication_outcome": "uncertain",
                "claims": {"has_replication_claims": False},
                "robustness": {
                    "mentions_bootstrap": False,
                    "mentions_monte_carlo": False,
                    "mentions_sensitivity_analysis": False,
                },
                "openness": {
                    "has_open_data": False,
                    "has_open_code": False,
                    "has_preregistration": False,
                },
                "upstream_signals": {
                    "has_statistical_content": False,
                    "p_value_count": 0,
                    "sample_size_count": 0,
                    "has_preregistration_methodology": False,
                    "has_references_section": False,
                    "estimated_reference_count": 0,
                },
                "overall_replication_score": 0.0,
            }

        # ---- Replication claims ----
        has_replication_claims = any(
            phrase in lowered
            for phrase in [
                "we replicate",
                "we replicated",
                "replication of prior work",
                "explicitly replicates prior findings",
                "replicate previous results",
                "direct replication",
                "conceptual replication",
            ]
        )
        claims = {"has_replication_claims": has_replication_claims}

        # ---- Robustness checks ----
        robustness = {
            "mentions_bootstrap": "bootstrap" in lowered or "bootstrapping" in lowered,
            "mentions_monte_carlo": "monte carlo" in lowered,
            "mentions_sensitivity_analysis": any(
                p in lowered
                for p in [
                    "sensitivity analysis",
                    "robustness check",
                    "stress test",
                ]
            ),
        }

        # ---- Openness / preregistration ----
        openness = {
            "has_open_data": any(
                p in lowered
                for p in [
                    "open data",
                    "data repository",
                    "osf.io",
                    "zenodo",
                    "figshare",
                    "dryad",
                ]
            ),
            "has_open_code": any(
                p in lowered
                for p in [
                    "analysis code",
                    "github.com",
                    "gitlab",
                    "code repository",
                ]
            ),
            "has_preregistration": any(
                p in lowered
                for p in [
                    "preregistered",
                    "registered report",
                    "preregistration",
                ]
            ),
        }

        # ---- Base scoring ----
        base = (
            (1.0 if has_replication_claims else 0.0)
            + sum(robustness.values()) / len(robustness)
            + sum(openness.values()) / len(openness)
        ) / 3.0

        # ---- Gentle upstream nudges ----
        nudge = 0.0
        if stats.get("has_statistical_content") and (stats.get("p_values") or {}).get("count", 0) > 0:
            nudge += 0.05
        if (methodology.get("sample_size") or {}).get("count", 0) > 0:
            nudge += 0.05
        if openness["has_preregistration"] or (methodology.get("transparency") or {}).get("has_preregistration"):
            nudge += 0.05
        if citations.get("has_references_section"):
            nudge += 0.02

        overall = float(max(0.0, min(1.0, base + nudge)))

        # ---- Outcome bucket ----
        if overall >= 0.67:
            outcome = "likely_replicable"
        elif overall <= 0.33:
            outcome = "fragile"
        else:
            outcome = "uncertain"

        return {
            "overall_replicability_score": overall,
            "simulated_replication_outcome": outcome,
            "claims": claims,
            "robustness": robustness,
            "openness": openness,
            "upstream_signals": {
                "has_statistical_content": bool(stats.get("has_statistical_content")),
                "p_value_count": int((stats.get("p_values") or {}).get("count", 0)),
                "sample_size_count": int((methodology.get("sample_size") or {}).get("count", 0)),
                "has_preregistration_methodology": bool(
                    (methodology.get("transparency") or {}).get("has_preregistration")
                ),
                "has_references_section": bool(citations.get("has_references_section")),
                "estimated_reference_count": int(citations.get("estimated_reference_count", 0)),
            },
            "overall_replication_score": overall,  # legacy alias
        }

    def analyze(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        return self.analyze_replication(text, **kwargs)
