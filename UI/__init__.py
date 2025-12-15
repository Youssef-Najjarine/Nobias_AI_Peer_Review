# UI/__init__.py
"""
Nobias AI Peer Review User Interface package

Contains the multi-page Streamlit application:
- Main dashboard (app.py)
- Submission portal
- Search interface
- Reviewer feedback viewer
"""

# Re-export pages for potential imports (optional but clean)
from . import dashboard
from .submission_portal import *
from .search_interface import *
from .reviewer_feedback_viewer import *

__all__ = [
    "dashboard",
    # Pages are discovered automatically by Streamlit — no need to list functions
]