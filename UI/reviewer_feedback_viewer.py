# UI/reviewer_feedback_viewer.py
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Nobias Reviewer Feedback", layout="centered")

st.title("🗣️ Reviewer Feedback Viewer")

st.markdown("Future: View community flags, comments, and replication attempts.")

st.info("Feedback system coming soon — part of Nobias collaborative review layer.")
st.write("Features planned:")
st.markdown("""
- Flag specific claims
- Add replication notes
- Vote on methodological concerns
- Community trust signals
""")

st.markdown("For now, all feedback is internal via self-audit and reasoning trace.")