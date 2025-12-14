# Tests/__init__.py
"""
Nobias_AI_Peer_Review test package.

This __init__.py enables:
- Proper test discovery by pytest
- Package-level imports in tests if needed
- Clean project structure in PyCharm
"""

# Import test modules to make them discoverable (optional but helpful)
from . import test_fraud_engine
from . import test_replication_engine
from . import test_review_flow

__all__ = [
    "test_fraud_engine",
    "test_replication_engine",
    "test_review_flow",
]