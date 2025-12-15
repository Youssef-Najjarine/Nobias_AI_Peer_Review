# Tests/__init__.py
"""
Nobias_AI_Peer_Review test package.

This __init__.py enables:
- Proper test discovery by pytest
- Package-level imports in tests if needed
- Clean project structure in PyCharm
"""

# Import all test modules for discovery
from . import test_review_flow
from . import test_replication_engine
from . import test_bias_detection
from . import test_statistical_analysis
from . import test_citation_validation
from . import test_security_layer
from . import test_hallucination_guard

__all__ = [
    "test_review_flow",
    "test_replication_engine",
    "test_bias_detection",
    "test_statistical_analysis",
    "test_citation_validation",
    "test_security_layer",
    "test_hallucination_guard",
]