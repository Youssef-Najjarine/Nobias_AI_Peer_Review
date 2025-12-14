# Evaluation/scoring/statistical_rigor_score.py
from typing import Dict, Any

class StatisticalRigorScorer:
    """
    Extracts statistical rigor score from StatisticalAnalyzer.
    """
    @staticmethod
    def score(statistics_result: Dict[str, Any]) -> float:
        score = statistics_result.get("overall_rigor_score", 0.0)
        return max(0.0, min(1.0, float(score)))