# Core/final_verdict_engine.py
from __future__ import annotations

from typing import Any, Dict, Tuple
import math


class FinalVerdictEngine:
    """
    Advanced final verdict builder with uncertainty propagation.
    Produces trust score + standard deviation + 95% confidence interval.
    """
    # Weights sum to 1.0
    _WEIGHTS: Dict[str, float] = {
        "statistics": 0.18,
        "methodology": 0.18,
        "citations": 0.12,
        "replication": 0.14,
        "bias": 0.08,
        "plagiarism": 0.10,
        "fraud": 0.10,
        "ethics": 0.10,
    }

    @staticmethod
    def _clamp01(x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def build(self, result: Dict[str, Any]) -> Dict[str, Any]:
        # Extract raw scores
        bias_score = float(result["bias"]["overall_bias_score"])
        stats_score = float(result["statistics"]["overall_rigor_score"])
        meth_score = float(result["methodology"]["overall_methodology_score"])
        cit_score = float(result["citations"]["overall_citation_quality_score"])
        repl_score = float(result["replication"]["overall_replicability_score"])
        plagiarism_suspicion = float(result["plagiarism"]["overall_plagiarism_suspicion_score"])
        fraud_suspicion = float(result["fraud"]["overall_fraud_suspicion_score"])
        ethics_risk = float(result["ethics"]["overall_ethics_risk_score"])

        # Invert "bad when high" scores
        plagiarism_good = 1.0 - plagiarism_suspicion
        fraud_good = 1.0 - fraud_suspicion
        ethics_good = 1.0 - ethics_risk
        bias_good = 1.0 - bias_score

        # Component "good" scores
        components = {
            "statistics": self._clamp01(stats_score),
            "methodology": self._clamp01(meth_score),
            "citations": self._clamp01(cit_score),
            "replication": self._clamp01(repl_score),
            "bias": self._clamp01(bias_good),
            "plagiarism": self._clamp01(plagiarism_good),
            "fraud": self._clamp01(fraud_good),
            "ethics": self._clamp01(ethics_good),
        }

        # Point estimate
        trust = sum(components[key] * weight for key, weight in self._WEIGHTS.items())
        trust = self._clamp01(trust)

        # === Uncertainty Propagation ===
        uncertainties = {
            "statistics": 0.15 if stats_score > 0.5 else 0.30,
            "methodology": 0.15 if meth_score > 0.5 else 0.30,
            "citations": 0.20 if cit_score > 0.6 else 0.35,
            "replication": 0.18 if repl_score > 0.6 else 0.32,
            "bias": 0.25,
            "plagiarism": 0.20,
            "fraud": 0.25,
            "ethics": 0.22,
        }

        variance = sum((self._WEIGHTS[key] ** 2) * (uncertainties[key] ** 2) for key in self._WEIGHTS)
        std_dev = math.sqrt(variance)
        ci_half_width = 1.96 * std_dev
        lower_ci = max(0.0, trust - ci_half_width)
        upper_ci = min(1.0, trust + ci_half_width)

        # Hard risk overrides
        overrides: list[str] = []
        if fraud_suspicion >= 0.70:
            overrides.append("High fraud/anomaly suspicion signals were detected.")
        if plagiarism_suspicion >= 0.70:
            overrides.append("High plagiarism/redundancy suspicion signals were detected.")
        if ethics_risk >= 0.70:
            overrides.append("High ethics/safety risk signals were detected.")
        if stats_score < 0.20 and meth_score < 0.20:
            overrides.append("Statistical and methodology support appears very weak.")

        label = "High Risk" if overrides else ("Reliable" if trust >= 0.70 else "Mixed" if trust >= 0.40 else "High Risk")

        reasons = self._build_reasons(result, trust, std_dev, lower_ci, upper_ci, label, overrides)

        return {
            "overall_trust_score": round(trust, 4),
            "trust_std_dev": round(std_dev, 4),
            "trust_95_confidence_interval": [round(lower_ci, 4), round(upper_ci, 4)],
            "verdict_label": label,
            "reasons": reasons,
        }

    @staticmethod
    def _build_reasons(
        result: Dict[str, Any],
        trust: float,
        std_dev: float,
        lower_ci: float,
        upper_ci: float,
        label: str,
        overrides: list[str],
    ) -> list[str]:
        stats = result["statistics"]
        meth = result["methodology"]
        cit = result["citations"]
        repl = result["replication"]
        plag = result["plagiarism"]
        fraud = result["fraud"]
        ethics = result["ethics"]

        stats_score = float(stats["overall_rigor_score"])
        meth_score = float(meth["overall_methodology_score"])
        cit_score = float(cit["overall_citation_quality_score"])
        repl_score = float(repl["overall_replicability_score"])
        plagiarism_suspicion = float(plag["overall_plagiarism_suspicion_score"])
        fraud_suspicion = float(fraud["overall_fraud_suspicion_score"])
        ethics_risk = float(ethics["overall_ethics_risk_score"])

        candidates: list[Tuple[int, str]] = []
        for o in overrides:
            candidates.append((100, o))

        if stats_score >= 0.70:
            candidates.append((60, "Strong statistical rigor signals were detected."))
        elif stats_score <= 0.25:
            candidates.append((70, "Statistical rigor signals were weak or missing."))

        if meth_score >= 0.60:
            candidates.append((55, "Methodology/design signals appear reasonably strong."))
        elif meth_score <= 0.25:
            candidates.append((65, "Methodology/design signals appear weak or underspecified."))

        if cit_score >= 0.60:
            candidates.append((40, "Citation/reference signals suggest decent sourcing."))
        elif cit_score <= 0.25:
            candidates.append((50, "Citation/reference signals are weak (few or unclear references)."))

        if repl_score >= 0.67:
            candidates.append((45, "Replicability signals are strong (robustness/openness/claims)."))
        elif repl_score <= 0.33:
            candidates.append((55, "Replicability signals are fragile (limited robustness/openness)."))

        if fraud_suspicion >= 0.50:
            candidates.append((80, "Fraud/anomaly heuristics raised notable concerns."))
        if plagiarism_suspicion >= 0.50:
            candidates.append((80, "Plagiarism/redundancy heuristics raised notable concerns."))
        if ethics_risk >= 0.50:
            candidates.append((80, "Ethics/safety heuristics raised notable concerns."))

        if stats.get("p_values", {}).get("count", 0) == 0 and stats_score <= 0.30:
            candidates.append((52, "Few or no p-values were detected; statistical reporting may be limited."))

        # Final verdict line with pre-computed CI values
        candidates.append((
            10,
            f"Final verdict: **{label}** (trust {trust:.3f} ± {std_dev:.3f}, 95% CI [{lower_ci:.3f}–{upper_ci:.3f}])"
        ))

        candidates.sort(key=lambda x: x[0], reverse=True)

        reasons: list[str] = []
        seen: set[str] = set()
        for _, text in candidates:
            if text not in seen:
                seen.add(text)
                reasons.append(text)
                if len(reasons) >= 5:
                    break

        if len(reasons) < 3:
            reasons.append("These signals are heuristic; interpret them as guidance, not proof.")
        if len(reasons) < 3:
            reasons.append("Consider a manual review of methods, data availability, and citations.")

        return reasons[:5]