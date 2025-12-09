# Core/statistical_analyzer.py

import re
from typing import Dict, List


class StatisticalAnalyzer:
    """
    Heuristic, transparent statistical rigor analyzer.

    This is not a full stats engine yet.
    It scans the text for:
      - p-values
      - confidence intervals
      - mentions of statistical tests
      - effect size / power terminology

    Then it computes a simple, interpretable "rigor" score in [0, 1].
    """

    # --- Public API ---

    def analyze(self, text: str) -> Dict:
        """
        Main entry point.
        Returns a dictionary summarizing statistical signals.
        """
        p_values = self._extract_p_values(text)
        ci_mentions = self._find_confidence_intervals(text)
        test_mentions = self._find_test_terms(text)
        effect_power_mentions = self._find_effect_power_terms(text)

        num_p = len(p_values)
        num_ci = len(ci_mentions)
        num_tests = len(test_mentions)
        num_effect_power = len(effect_power_mentions)

        # Basic signals
        has_stats = num_p > 0 or num_ci > 0 or num_tests > 0

        # Very simple interpretation:
        # - More diverse reporting (p-values + CIs + tests + effect size/power)
        #   -> higher rigor score.
        # - But we cap it at 1.0 for interpretability.
        diversity_components = 0
        if num_p > 0:
            diversity_components += 1
        if num_ci > 0:
            diversity_components += 1
        if num_tests > 0:
            diversity_components += 1
        if num_effect_power > 0:
            diversity_components += 1

        diversity_score = diversity_components / 4.0  # 0.0 to 1.0

        # Slight bonus if multiple p-values are reported
        multiplicity_bonus = min(num_p / 10.0, 0.3)  # cap bonus

        overall_rigor_score = min(diversity_score + multiplicity_bonus, 1.0)

        return {
            "has_statistical_content": has_stats,
            "p_values": {
                "count": num_p,
                "values": p_values,
            },
            "confidence_intervals": {
                "count": num_ci,
                "examples": ci_mentions[:5],
            },
            "test_terms": {
                "count": num_tests,
                "examples": test_mentions[:10],
            },
            "effect_size_and_power_terms": {
                "count": num_effect_power,
                "examples": effect_power_mentions[:10],
            },
            "diversity_score": diversity_score,
            "overall_rigor_score": overall_rigor_score,
        }

    # --- Internal helpers ---

    def _extract_p_values(self, text: str) -> List[float]:
        """
        Finds patterns like:
          p < 0.05
          p=0.012
          p <= 0.001
        Returns a list of numeric p-values (as floats) when possible.
        """
        # case-insensitive
        pattern = re.compile(
            r"p\s*([<>=]{1,2})\s*(0\.\d+|0|1\.0+|1)",
            re.IGNORECASE
        )
        matches = pattern.findall(text)

        p_values = []
        for op, val_str in matches:
            try:
                value = float(val_str)
            except ValueError:
                continue
            # We don't currently use the operator, but we could later
            p_values.append(value)

        return p_values

    def _find_confidence_intervals(self, text: str) -> List[str]:
        """
        Look for textual patterns that resemble confidence intervals, e.g.:
          95% CI [1.2, 2.3]
          90 % confidence interval (0.1, 0.5)
        Returns the raw snippets.
        """
        ci_patterns = [
            r"\d{2}\s*%\s*CI\s*\[[^\]]+\]",
            r"\d{2}\s*%\s*confidence interval\s*\([^)]+\)",
        ]
        results: List[str] = []
        for pat in ci_patterns:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                results.append(m.group(0))
        return results

    def _find_test_terms(self, text: str) -> List[str]:
        """
        Find mentions of common statistical tests.
        """
        terms = [
            "t-test", "t test", "student's t",
            "anova", "analysis of variance",
            "chi-square", "chi squared", "χ2",
            "mann-whitney", "wilcoxon",
            "regression", "linear regression",
            "logistic regression",
        ]
        lowered = text.lower()
        hits = []
        for term in terms:
            if term.lower() in lowered:
                hits.append(term)
        return hits

    def _find_effect_power_terms(self, text: str) -> List[str]:
        """
        Find mentions of effect size and statistical power concepts.
        """
        terms = [
            "effect size", "cohen's d", "eta squared", "η2",
            "partial eta squared", "odds ratio", "hazard ratio",
            "statistical power", "power analysis", "sample size calculation",
        ]
        lowered = text.lower()
        hits = []
        for term in terms:
            if term.lower() in lowered:
                hits.append(term)
        return hits
