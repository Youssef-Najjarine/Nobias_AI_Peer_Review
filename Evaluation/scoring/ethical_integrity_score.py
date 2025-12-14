# Evaluation/scoring/ethical_integrity_score.py
from typing import Dict, Any

class EthicalIntegrityScorer:
    """
    Inverts ethics risk → higher score = better (lower risk).
    """
    @staticmethod
    def score(ethics_result: Dict[str, Any]) -> float:
        risk = ethics_result.get("overall_ethics_risk_score", 0.0)
        return max(0.0, min(1.0, 1.0 - float(risk)))