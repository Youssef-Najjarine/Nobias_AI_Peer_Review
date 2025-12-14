# Core/final_verdict_engine.py

from __future__ import annotations

from typing import Any


class FinalVerdictEngine:
    """
    Product-style final verdict builder.

    Consumes Option A outputs from:
      - bias
      - statistics
      - methodology
      - citations
      - plagiarism
      - fraud
      - ethics
      - replication

    Produces:
      - overall_trust_score (0..1, higher is better)
      - verdict_label ("Reliable" | "Mixed" | "High Risk")
      - reasons (3–5 bullets)
    """

    # Weights sum to 1.0
    _WEIGHTS: dict[str, float] = {
        "statistics": 0.18,
        "methodology": 0.18,
        "citations": 0.12,
        "replication": 0.14,
        "bias": 0.08,
        "plagiarism": 0.10,  # inverted (lower suspicion => better)
        "fraud": 0.10,       # inverted (lower suspicion => better)
        "ethics": 0.10,      # inverted (lower risk => better)
    }

    @staticmethod
    def _clamp01(x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def build(self, result: dict[str, Any]) -> dict[str, Any]:
        # ---- Pull Option A scores ----
        bias_score = float(result["bias"]["overall_bias_score"])
        stats_score = float(result["statistics"]["overall_rigor_score"])
        meth_score = float(result["methodology"]["overall_methodology_score"])
        cit_score = float(result["citations"]["overall_citation_quality_score"])
        repl_score = float(result["replication"]["overall_replicability_score"])

        plagiarism_suspicion = float(result["plagiarism"]["overall_plagiarism_suspicion_score"])
        fraud_suspicion = float(result["fraud"]["overall_fraud_suspicion_score"])
        ethics_risk = float(result["ethics"]["overall_ethics_risk_score"])

        # Convert “bad when high” into “good when high”
        plagiarism_good = 1.0 - plagiarism_suspicion
        fraud_good = 1.0 - fraud_suspicion
        ethics_good = 1.0 - ethics_risk

        # Bias is “bad when high” (even if often small), so invert.
        bias_good = 1.0 - bias_score

        parts: dict[str, float] = {
            "statistics": self._clamp01(stats_score),
            "methodology": self._clamp01(meth_score),
            "citations": self._clamp01(cit_score),
            "replication": self._clamp01(repl_score),
            "bias": self._clamp01(bias_good),
            "plagiarism": self._clamp01(plagiarism_good),
            "fraud": self._clamp01(fraud_good),
            "ethics": self._clamp01(ethics_good),
        }

        # Weighted trust score
        trust = 0.0
        for key, weight in self._WEIGHTS.items():
            trust += parts[key] * weight
        trust = self._clamp01(trust)

        # ---- Hard “risk overrides” ----
        overrides: list[str] = []

        if fraud_suspicion >= 0.70:
            overrides.append("High fraud/anomaly suspicion signals were detected.")
        if plagiarism_suspicion >= 0.70:
            overrides.append("High plagiarism/redundancy suspicion signals were detected.")
        if ethics_risk >= 0.70:
            overrides.append("High ethics/safety risk signals were detected.")

        if stats_score < 0.20 and meth_score < 0.20:
            overrides.append("Statistical and methodology support appears very weak.")

        # ---- Verdict label thresholds ----
        if overrides:
            label = "High Risk"
        else:
            if trust >= 0.70:
                label = "Reliable"
            elif trust <= 0.40:
                label = "High Risk"
            else:
                label = "Mixed"

        reasons = self._build_reasons(
            result=result,
            trust=trust,
            label=label,
            overrides=overrides,
        )

        return {
            "overall_trust_score": trust,
            "verdict_label": label,
            "reasons": reasons,
        }

    @staticmethod
    def _build_reasons(
        result: dict[str, Any],
        trust: float,
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

        candidates: list[tuple[int, str]] = []

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

        candidates.append((10, f"Final verdict: **{label}** (trust score `{trust:.2f}` out of 1.00)."))

        candidates.sort(key=lambda x: x[0], reverse=True)

        reasons: list[str] = []
        seen: set[str] = set()

        for _, text in candidates:
            if text in seen:
                continue
            seen.add(text)
            reasons.append(text)
            if len(reasons) >= 5:
                break

        if len(reasons) < 3:
            reasons.append("These signals are heuristic; interpret them as guidance, not proof.")
        if len(reasons) < 3:
            reasons.append("Consider a manual review of methods, data availability, and citations.")

        return reasons[:5]
