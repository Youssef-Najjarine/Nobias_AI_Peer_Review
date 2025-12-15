# Ai_Models/__init__.py
"""
Ai_Models package — Advanced, deterministic models extending Core engines.
No external LLMs — fully transparent and auditable.
"""

from .hallucination_detector import HallucinationDetector
from .reviewer_llm import ReviewerLLMStub
from .bias_head import BiasHead
from .ethics_guard import EthicsGuardModel
from .replicability_model import ReplicabilityModel
from .citation_chain_model import CitationChainModel

__all__ = [
    "HallucinationDetector",
    "ReviewerLLMStub",
    "BiasHead",
    "EthicsGuardModel",
    "ReplicabilityModel",
    "CitationChainModel",
]