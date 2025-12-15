# UI/dashboard/__init__.py
"""
Nobias AI Peer Review Dashboard submodule

Contains the main dashboard page (app.py) and supporting assets/graphs.
"""

# Make the main app importable if needed
from .app import *

__all__ = [
    "app",  # Exposes the main Streamlit page
]