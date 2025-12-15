# UI/dashboard/__init__.py
"""
Nobias AI Peer Review Dashboard
Interactive Streamlit front-end for paper submission and review visualization.
"""

# This makes the dashboard script importable if needed
from .peer_review_dashboard import *  # noqa: F403

__all__ = ["peer_review_dashboard"]