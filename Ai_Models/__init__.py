# Ai_Models/__init__.py
"""
Ai_Models package — specialized AI-related audit and detection models
that support the core review engine without introducing external LLM dependencies.
"""

from .hallucination_detector import HallucinationDetector

__all__ = [
    "HallucinationDetector",
]