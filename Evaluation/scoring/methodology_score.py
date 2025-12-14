# Evaluation/scoring/methodology_score.py
from typing import Dict, Any

class MethodologyScorer:
    """
    Extracts methodology score from MethodologyValidator.
    """
    @staticmethod
    def score(methodology_result: Dict[str, Any]) -> float:
        score = methodology_result.get("overall_methodology_score", 0.0)
        return max(0.0, min(1.0, float(score)))