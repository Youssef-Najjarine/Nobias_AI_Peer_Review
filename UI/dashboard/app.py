# UI/dashboard/app.py
from __future__ import annotations

import streamlit as st
from pathlib import Path

from Core.review_engine import ReviewEngine
from Core.report_generator import ReportGenerator
from Core.ingestion.ingestor import DocumentIngestor

# Page config
st.set_page_config(
    page_title="Nobias AI Peer Review",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Initialize core
engine = ReviewEngine()
report_generator = ReportGenerator(output_dir="reports")
ingestor = DocumentIngestor()

# Directories
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

# Title & Header
st.title("🚀 Nobias AI Peer Review")
st.markdown("""
**A transparent, incorruptible, self-auditing scientific referee.**

Upload a paper (PDF or text) and receive a full bias-free review with:
- Trust score & verdict
- Bias, replicability, methodology, fraud, ethics analysis
- Full reasoning trace
- Self-audit for hallucinations and overconfidence
""")

# Sidebar
with st.sidebar:
    st.header("About Nobias")
    st.markdown("""
    Nobias removes gatekeeping from science.

    No author name. No institution. No prestige.

    Only the content matters.
    """)
    st.info("Built by Youssef — December 2025")

# Main upload area
st.subheader("Submit a Paper")
uploaded_file = st.file_uploader("Upload PDF or text file", type=["pdf", "txt", "md"])
paper_text = st.text_area("Or paste raw text here", height=200)
paper_name = st.text_input("Paper name (optional)", placeholder="e.g., My Breakthrough Study")

col1, col2 = st.columns([1, 3])
submit = col1.button("Review Paper", type="primary", use_container_width=True)
clear = col2.button("Clear", use_container_width=True)

if clear:
    st.experimental_rerun()

if submit:
    if not uploaded_file and not paper_text.strip():
        st.error("Please upload a file or paste text.")
    else:
        with st.spinner("Nobias is reviewing your paper... This may take 10–30 seconds."):
            try:
                if uploaded_file:
                    # Save temporarily
                    temp_path = Path("uploads") / uploaded_file.name
                    temp_path.parent.mkdir(exist_ok=True)
                    temp_path.write_bytes(uploaded_file.getvalue())
                    doc = ingestor.ingest(temp_path)
                    result = engine.review_paper(doc)
                else:
                    result = engine.review_paper(paper_text)

                name = paper_name or uploaded_file.name or "unnamed_paper"
                report_path = report_generator.save_markdown(name, result)

                # Success!
                st.success("Review Complete!")

                # Final Verdict
                verdict = result["final_verdict"]
                trust = verdict["overall_trust_score"]
                label = verdict["verdict_label"]

                col1, col2, col3 = st.columns(3)
                col1.metric("Trust Score", f"{trust:.3f}")
                col2.metric("Verdict", label)
                col3.metric("Hallucination Risk",
                            f"{result['hallucination_audit'].get('overall_hallucination_risk', 0):.3f}")

                # Report
                st.subheader("Full Review Report")
                report_file = REPORT_DIR / report_path.name
                if report_file.exists():
                    report_md = report_file.read_text(encoding="utf-8")
                    st.markdown(report_md)

                    with open(report_file, "rb") as f:
                        st.download_button(
                            "Download Report (Markdown)",
                            f,
                            file_name=report_path.name,
                            mime="text/markdown",
                        )
                else:
                    st.warning("Report generated but not found. Please refresh.")

                # Reasoning Trace (collapsible)
                with st.expander("View Full Reasoning Trace"):
                    for step in result["trace"]:
                        tag = step["tag"]
                        desc = step["description"]
                        meta = step.get("metadata", {})
                        conf = step.get("confidence")
                        line = f"**[{tag.upper()}]** {desc}"
                        if conf:
                            line += f" (Confidence: {conf})"
                        st.write(line)
                        if meta:
                            st.json(meta)

            except Exception as e:
                st.error(f"Review failed: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.caption("Nobias AI Peer Review — Replacing broken gatekeeping with transparent truth. December 2025.")