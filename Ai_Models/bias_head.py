# Ai_Models/bias_head.py
from __future__ import annotations

from typing import Dict, Any

class BiasHead:
    """
    Specialized head for bias detection — wraps Core BiasDetector.
    Future: hyperdimensional or symbolic encoding.
    """
    def __init__(self):
        from Core.bias_detector import BiasDetector
        self.detector = BiasDetector()

    def analyze(self, text: str) -> Dict[str, Any]:
        result = self.detector.analyze_text(text)
        result["enhanced_flags"] = []
        if result["overall_bias_score"] > 0.4:
            result["enhanced_flags"].append("High emotional/authority language detected")
        return result