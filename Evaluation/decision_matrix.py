# Evaluation/decision_matrix.py
from typing import Dict, Any
from Evaluation.scoring.bias_score import BiasScorer
from Evaluation.scoring.replicability_score import ReplicabilityScorer
from Evaluation.scoring.methodology_score import MethodologyScorer
from Evaluation.scoring.statistical_rigor_score import StatisticalRigorScorer
from Evaluation.scoring.ethical_integrity_score import EthicalIntegrityScorer

class DecisionMatrix:
    """
    Final aggregation layer (alternative/complement to FinalVerdictEngine).
    Produces trust score and structured decision.
    """
    WEIGHTS = {
        "statistics": 0.20,
        "methodology": 0.20,
        "replicability": 0.18,
        "citations": 0.12,
        "bias": 0.08,        # inverted
        "plagiarism": 0.08,  # inverted
        "fraud": 0.08,       # inverted
        "ethics": 0.06,      # inverted
    }

    @staticmethod
    def compute_trust(result: Dict[str, Any]) -> Dict[str, Any]:
        stats = StatisticalRigorScorer.score(result["statistics"])
        meth = MethodologyScorer.score(result["methodology"])
        repl = ReplicabilityScorer.score(result["replication"])
        cit = result["citations"].get("overall_citation_quality_score", 0.0)
        bias = 1.0 - BiasScorer.score(result["bias"])
        plag = 1.0 - result["plagiarism"].get("overall_plagiarism_suspicion_score", 0.0)
        fraud = 1.0 - result["fraud"].get("overall_fraud_suspicion_score", 0.0)
        ethics = EthicalIntegrityScorer.score(result["ethics"])

        trust = (
            DecisionMatrix.WEIGHTS["statistics"] * stats +
            DecisionMatrix.WEIGHTS["methodology"] * meth +
            DecisionMatrix.WEIGHTS["replicability"] * repl +
            DecisionMatrix.WEIGHTS["citations"] * cit +
            DecisionMatrix.WEIGHTS["bias"] * bias +
            DecisionMatrix.WEIGHTS["plagiarism"] * plag +
            DecisionMatrix.WEIGHTS["fraud"] * fraud +
            DecisionMatrix.WEIGHTS["ethics"] * ethics
        )

        trust = max(0.0, min(1.0, trust))

        label = "Reliable" if trust >= 0.70 else "Mixed" if trust >= 0.40 else "High Risk"

        return {
            "overall_trust_score": round(trust, 4),
            "verdict": label,
            "component_scores": {
                "statistics": round(stats, 4),
                "methodology": round(meth, 4),
                "replicability": round(repl, 4),
                "citations": round(cit, 4),
                "bias_good": round(bias, 4),
                "plagiarism_good": round(plag, 4),
                "fraud_good": round(fraud, 4),
                "ethics_good": round(ethics, 4),
            }
        }