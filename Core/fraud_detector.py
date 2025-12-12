# Core/fraud_detector.py

from __future__ import annotations

import re
from typing import Dict, Any, List


class FraudDetector:
    """
    Lightweight, rule-based fraud / anomaly detector (Option A schema).

    Returns:
      - overall_fraud_suspicion_score: float in [0, 1]
      - impossible_p_values: {count, examples}
      - suspicious_p_clustering: {count, cluster_ratio, examples}
      - extreme_effect_language: {count, examples}
      - mismatched_p_text: {count, examples}
      - signals: {refuses_data_sharing, identical_p_values_pattern, manual_adjustment_language, p_hacking_language}

    Also includes legacy key:
      - suspiciousness_score (alias of overall_fraud_suspicion_score)
    """

    _P_VALUE_RE = re.compile(
        r"""
        p\s*
        (?:=|<=|>=|<|>)
        \s*
        (?P<val>(?:0?\.\d+)|(?:1(?:\.0+)?)|(?:0))
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    _SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

    def analyze_fraud(self, text: str) -> Dict[str, Any]:
        text = text or ""
        lowered = text.lower().strip()

        # Empty text: perfectly clean
        if not lowered:
            return {
                "overall_fraud_suspicion_score": 0.0,
                "impossible_p_values": {"count": 0, "examples": []},
                "suspicious_p_clustering": {"count": 0, "cluster_ratio": 0.0, "examples": []},
                "extreme_effect_language": {"count": 0, "examples": []},
                "mismatched_p_text": {"count": 0, "examples": []},
                "signals": {
                    "refuses_data_sharing": False,
                    "identical_p_values_pattern": False,
                    "manual_adjustment_language": False,
                    "p_hacking_language": False,
                },
                "suspiciousness_score": 0.0,  # legacy alias
            }

        # ---- Your existing signals (kept) ----
        refuses_data_sharing = any(
            phrase in lowered
            for phrase in [
                "we do not share raw data",
                "we do not share data",
                "data cannot be shared",
                "data cannot be made public",
                "due to proprietary concerns",
                "cannot release the raw data",
                "data not available",
                "code not available",
            ]
        )

        identical_p_values_pattern = any(
            phrase in lowered
            for phrase in [
                "all 37 tests yielded p = 0.049",
                "all tests yielded p = 0.049",
                "identical p-values",
                "same p-value for all tests",
            ]
        )

        manual_adjustment_language = any(
            phrase in lowered
            for phrase in [
                "manually adjusted",
                "manually modified",
                "manually corrected",
                "adjusted to better reflect the theory",
                "tuned the data",
                "observations were manually adjusted",
                "data were adjusted",
            ]
        )

        p_hacking_language = any(
            phrase in lowered
            for phrase in [
                "after inspecting the data we adjusted",
                "after looking at the data we decided",
                "after seeing the initial results",
                "ran multiple analyses until",
                "repeatedly re-ran tests until",
                "post hoc",
                "removed outliers",
                "excluding outliers",
                "multiple comparisons",
            ]
        )

        signals: Dict[str, bool] = {
            "refuses_data_sharing": refuses_data_sharing,
            "identical_p_values_pattern": identical_p_values_pattern,
            "manual_adjustment_language": manual_adjustment_language,
            "p_hacking_language": p_hacking_language,
        }

        # ---- Option A buckets ----

        # 1) impossible_p_values (very basic: flag p < 0 or > 1 if present)
        impossible: List[str] = []
        for m in self._P_VALUE_RE.finditer(text):
            raw = m.group(0).strip()
            try:
                v = float(m.group("val"))
            except ValueError:
                continue
            if v < 0.0 or v > 1.0:
                impossible.append(raw)

        impossible_p_values = {"count": len(impossible), "examples": impossible[:10]}

        # 2) suspicious_p_clustering (p in [0.045, 0.05])
        all_p_vals: List[float] = []
        cluster_examples: List[str] = []
        for m in self._P_VALUE_RE.finditer(text):
            raw = m.group(0).strip()
            try:
                v = float(m.group("val"))
            except ValueError:
                continue
            all_p_vals.append(v)
            if 0.045 <= v <= 0.05 and len(cluster_examples) < 10:
                cluster_examples.append(raw)

        cluster_ratio = (len(cluster_examples) / max(len(all_p_vals), 1)) if all_p_vals else 0.0
        suspicious_p_clustering = {
            "count": len(cluster_examples),
            "cluster_ratio": float(cluster_ratio),
            "examples": cluster_examples,
        }

        # 3) extreme_effect_language (simple keyword hits)
        extreme_terms = [
            "groundbreaking",
            "unprecedented",
            "clearly proves",
            "obvious that",
            "definitively",
            "revolutionary",
            "no doubt",
        ]
        extreme_hits = [t for t in extreme_terms if t in lowered]
        extreme_effect_language = {"count": len(extreme_hits), "examples": extreme_hits[:10]}

        # 4) mismatched_p_text (simple heuristic)
        # If sentence says "significant" with p>0.05 or "not significant" with p<=0.05
        mismatches: List[str] = []
        for s in self._SENTENCE_SPLIT_RE.split(text):
            sl = s.lower()
            if "p" not in sl:
                continue
            m = self._P_VALUE_RE.search(s)
            if not m:
                continue
            try:
                v = float(m.group("val"))
            except ValueError:
                continue

            claims_sig = ("significant" in sl) and ("not significant" not in sl)
            claims_nonsig = "not significant" in sl or "non-significant" in sl

            if claims_sig and v > 0.05:
                mismatches.append(s.strip())
            if claims_nonsig and v <= 0.05:
                mismatches.append(s.strip())

        mismatched_p_text = {"count": len(mismatches), "examples": mismatches[:5]}

        # ---- Score (bounded) ----
        signals_score = sum(1 for v in signals.values() if v) / len(signals)
        cluster_score = min(1.0, suspicious_p_clustering["cluster_ratio"] * 2.0)  # 0.5 ratio => 1.0
        mismatch_score = min(1.0, mismatched_p_text["count"] / 3.0)
        impossible_score = 1.0 if impossible_p_values["count"] > 0 else 0.0
        extreme_score = min(0.5, extreme_effect_language["count"] / 4.0)

        overall = (
            0.35 * signals_score
            + 0.25 * cluster_score
            + 0.20 * mismatch_score
            + 0.10 * impossible_score
            + 0.10 * extreme_score
        )
        overall = float(max(0.0, min(1.0, overall)))

        return {
            "overall_fraud_suspicion_score": overall,
            "impossible_p_values": impossible_p_values,
            "suspicious_p_clustering": suspicious_p_clustering,
            "extreme_effect_language": extreme_effect_language,
            "mismatched_p_text": mismatched_p_text,
            "signals": signals,
            "suspiciousness_score": overall,  # legacy alias (keeps your existing tests happy if any rely on it)
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        return self.analyze_fraud(text)
