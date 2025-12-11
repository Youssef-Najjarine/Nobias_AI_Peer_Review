# Core/fraud_detector.py

import re
from typing import Dict, Any, List
from collections import Counter


class FraudDetector:
    """
    Heuristic fraud / anomaly detector for statistical reporting.

    This is NOT a legal or absolute claim of fraud.
    It just flags suspicious patterns like:
      - impossible / highly odd p-values (e.g., p = 0.000)
      - strong clustering of p-values just below 0.05
      - extreme "too good to be true" language around results
      - text patterns that mention thresholds oddly

    Output:
      - impossible_p_values: {count, examples}
      - suspicious_p_clustering: {count, examples}
      - extreme_effect_language: {count, examples}
      - mismatched_p_text: {count, examples}
      - overall_fraud_suspicion_score in [0, 1]
    """

    P_PATTERN = re.compile(r"p\s*([<=>])\s*(0\.\d+|1\.0+|0\.0+)", re.IGNORECASE)

    def _find_p_values(self, text: str) -> List[float]:
        values = []
        for match in self.P_PATTERN.finditer(text):
            _, num_str = match.groups()
            try:
                val = float(num_str)
                values.append(val)
            except ValueError:
                continue
        return values

    def _find_impossible_or_odds(self, text: str) -> Dict[str, Any]:
        examples = []
        count = 0
        for match in self.P_PATTERN.finditer(text):
            full = match.group(0)
            op, num_str = match.groups()
            try:
                val = float(num_str)
            except ValueError:
                continue

            # Suspicious if exactly 0, exactly 1, or < 0 or > 1
            if val < 0.0 or val > 1.0 or abs(val) < 1e-6 or abs(val - 1.0) < 1e-6:
                count += 1
                if len(examples) < 5:
                    examples.append(full.strip())

        return {
            "count": count,
            "examples": examples,
        }

    def _check_p_clustering(self, p_values: List[float]) -> Dict[str, Any]:
        """
        Look for clustering of p-values right below 0.05,
        e.g., many p's between 0.045 and 0.050.
        """
        if not p_values:
            return {"count": 0, "examples": [], "cluster_ratio": 0.0}

        cluster_vals = [p for p in p_values if 0.045 <= p < 0.05]
        count = len(cluster_vals)
        ratio = count / len(p_values)

        examples = [f"p={p:.3f}" for p in cluster_vals[:5]]

        return {
            "count": count,
            "examples": examples,
            "cluster_ratio": ratio,
        }

    def _find_extreme_effect_language(self, text: str) -> Dict[str, Any]:
        """
        Looks for "too good to be true" phrasing near results.
        """
        extreme_terms = [
            "undeniable evidence",
            "irrefutable proof",
            "conclusive proof",
            "perfect prediction",
            "zero error",
            "flawless",
            "miraculous",
            "too good to be true",
        ]
        lowered = text.lower()
        examples = []
        count = 0
        for term in extreme_terms:
            if term in lowered:
                count += lowered.count(term)
                if len(examples) < 5:
                    examples.append(term)
        return {
            "count": count,
            "examples": examples,
        }

    def _find_mismatched_p_text(self, text: str) -> Dict[str, Any]:
        """
        Very crude heuristic: if a sentence mentions p < 0.05 and also
        contains an explicitly larger p-value (e.g., p = 0.08), flag it.
        """
        sentences = re.split(r"[.!?]+", text)
        suspicious_sentences = []

        for raw in sentences:
            s = raw.strip()
            if not s:
                continue
            s_lower = s.lower()

            if "p < 0.05" in s_lower or "p<=0.05" in s_lower or "p ≤ 0.05" in s_lower:
                # Find all numeric p= values in this sentence
                p_vals = self._find_p_values(s_lower)
                # If any are >= 0.06, that's fishy
                if any(p >= 0.06 for p in p_vals):
                    if len(suspicious_sentences) < 5:
                        suspicious_sentences.append(s)

        return {
            "count": len(suspicious_sentences),
            "examples": suspicious_sentences,
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        if not text.strip():
            return {
                "impossible_p_values": {"count": 0, "examples": []},
                "suspicious_p_clustering": {
                    "count": 0,
                    "examples": [],
                    "cluster_ratio": 0.0,
                },
                "extreme_effect_language": {"count": 0, "examples": []},
                "mismatched_p_text": {"count": 0, "examples": []},
                "overall_fraud_suspicion_score": 0.0,
            }

        # Extract list of p-values once
        p_values = self._find_p_values(text)

        # Components
        impossible_info = self._find_impossible_or_odds(text)
        cluster_info = self._check_p_clustering(p_values)
        extreme_info = self._find_extreme_effect_language(text)
        mismatch_info = self._find_mismatched_p_text(text)

        # ------------------------------------------------------------------
        # Scoring heuristic (bounded [0, 1])
        # ------------------------------------------------------------------
        score = 0.0

        # Impossible / extreme p-values: strong signal (up to 0.4)
        score += min(0.4, 0.1 * impossible_info["count"])

        # Clustering near threshold: moderate signal (up to 0.3)
        score += min(0.3, cluster_info["cluster_ratio"] * 0.75)

        # Extreme language: moderate (up to 0.2)
        score += min(0.2, extreme_info["count"] * 0.05)

        # Mismatched text: strong but rare signal (up to 0.3)
        score += min(0.3, mismatch_info["count"] * 0.15)

        score = max(0.0, min(1.0, score))

        return {
            "impossible_p_values": impossible_info,
            "suspicious_p_clustering": cluster_info,
            "extreme_effect_language": extreme_info,
            "mismatched_p_text": mismatch_info,
            "overall_fraud_suspicion_score": score,
        }
