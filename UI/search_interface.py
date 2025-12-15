# UI/search_interface.py
from __future__ import annotations

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Nobias Search", layout="wide")

st.title("🔍 Nobias Review Archive Search")

reports_dir = Path("reports")
reports = sorted(reports_dir.glob("*.md"), reverse=True)

if not reports:
    st.info("No reviews yet. Submit a paper first!")
else:
    search = st.text_input("Search reports")
    filtered = [r for r in reports if search.lower() in r.name.lower()]

    for report in filtered:
        with st.expander(f"📑 {report.stem}"):
            content = report.read_text(encoding="utf-8")
            st.markdown(content[:2000] + ("..." if len(content) > 2000 else ""))
            with open(report, "rb") as f:
                st.download_button("Download Full", f, file_name=report.name, key=report.name)