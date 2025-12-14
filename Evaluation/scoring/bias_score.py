# Evaluation/scoring/bias_score.py
from Core.bias_detector import BiasDetector
from typing import Dict, Any

class BiasScorer:
    """
    Converts raw BiasDetector output into a normalized [0, 1] score
    where 1.0 = highest bias (worst), 0.0 = neutral/clean.
    This is used by FinalVerdictEngine.
    """
    @staticmethod
    def score(bias_result: Dict[str, Any]) -> float:
        raw = bias_result.get("overall_bias_score", 0.0)
        # Already bounded [0,1], but ensure float
        return max(0.0, min(1.0, float(raw)))