# Ai_Models/ethics_guard.py
from __future__ import annotations

from typing import Dict, Any

class EthicsGuardModel:
    """
    Advanced ethics model — extends Core EthicsGuard.
    Future: dual-use research detection via knowledge graph.
    """
    def __init__(self):
        from Core.ethics_guard import EthicsGuard
        self.guard = EthicsGuard()

    def analyze(self, text: str) -> Dict[str, Any]:
        result = self.guard.analyze(text)
        if result["overall_ethics_risk_score"] > 0.5:
            result["recommendation"] = "Flag for human ethics review"
        else:
            result["recommendation"] = "Low ethics risk"
        return result