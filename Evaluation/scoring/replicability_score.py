# Evaluation/scoring/replicability_score.py
from typing import Dict, Any

class ReplicabilityScorer:
    """
    Extracts replicability score from ReplicationSimulator output.
    """
    @staticmethod
    def score(replication_result: Dict[str, Any]) -> float:
        score = replication_result.get("overall_replicability_score", 0.0)
        return max(0.0, min(1.0, float(score)))