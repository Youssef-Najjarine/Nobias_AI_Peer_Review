# Core/statistical_analyzer.py

import re
from typing import Dict, Any


class StatisticalAnalyzer:
    """
    Detects statistical signals:
        - p-values
        - confidence intervals
        - test names
        - effect size and power analysis terms

    Now improved:
        has_statistical_content returns True if ANY of the above are found.
    """

    P_VALUE_PATTERN = re.compile(r"\bp\s*[<=>]\s*0\.\d+", re.IGNORECASE)
    CI_PATTERN = re.compile(r"\b\d+%\s*CI\b|\bCI\s*\[", re.IGNORECASE)

    TEST_TERMS = [
        "t-test", "t test", "anova", "regression", "chi-square", "chi square",
        "manova", "wilcoxon", "kruskal-wallis", "pearson correlation",
        "spearman correlation", "mixed model", "linear model"
    ]

    EFFECT_AND_POWER_TERMS = [
        "effect size", "cohen's d", "eta-squared", "eta squared",
        "standardized effect", "power analysis", "statistical power",
        "hedges g", "omega-squared"
    ]

    def analyze(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()

        # --- P-values ---
        p_values = self.P_VALUE_PATTERN.findall(text_lower)
        p_value_count = len(p_values)

        # --- Confidence intervals ---
        ci_matches = self.CI_PATTERN.findall(text_lower)
        ci_count = len(ci_matches)

        # --- Tests ---
        tests_present = [t for t in self.TEST_TERMS if t in text_lower]
        has_tests = len(tests_present) > 0

        # --- Effect sizes + power ---
        effect_terms_present = [t for t in self.EFFECT_AND_POWER_TERMS if t in text_lower]
        has_effect_terms = len(effect_terms_present) > 0

        # ---------------------------------------------------------------------
        # 🔥 UPDATED LOGIC:
        # "Statistical content" means ANY recognizable statistical element.
        # ---------------------------------------------------------------------
        has_statistical_content = (
            p_value_count > 0
            or ci_count > 0
            or has_tests
            or has_effect_terms
        )

        # ---------------------------------------------------------------------
        # Rigor scoring:
        #   Counts how many categories are present:
        #       p-values
        #       confidence intervals
        #       tests
        #       effect-size/power terms
        # ---------------------------------------------------------------------
        categories_present = sum([
            p_value_count > 0,
            ci_count > 0,
            has_tests,
            has_effect_terms
        ])

        diversity_score = categories_present / 4  # 0 → 1.0
        bonus = min(p_value_count, 5) * 0.05       # up to +0.25
        overall_rigor = min(1.0, diversity_score + bonus)

        return {
            "has_statistical_content": has_statistical_content,
            "p_values": {
                "count": p_value_count,
                "examples": p_values[:5]
            },
            "confidence_intervals": {
                "count": ci_count,
                "examples": ci_matches[:5]
            },
            "tests": tests_present[:10],
            "effect_terms": effect_terms_present[:10],
            "overall_rigor_score": overall_rigor,
            "raw": {
                "p_value_count": p_value_count,
                "ci_count": ci_count,
                "has_tests": has_tests,
                "has_effect_terms": has_effect_terms
            }
        }
