# UI/submission_portal.py
from __future__ import annotations

import streamlit as st
from Core.review_engine import ReviewEngine
from Core.report_generator import ReportGenerator
from Core.ingestion.ingestor import DocumentIngestor
from pathlib import Path

st.set_page_config(page_title="Nobias Submission Portal", layout="centered")

st.title("📄 Nobias Submission Portal")
st.markdown("Submit your paper for transparent, bias-free review.")

engine = ReviewEngine()
report_generator = ReportGenerator()
ingestor = DocumentIngestor()

uploaded_file = st.file_uploader("Upload PDF or text", type=["pdf", "txt", "md"])
paper_text = st.text_area("Or paste text", height=300)
paper_name = st.text_input("Paper name (optional)")

if st.button("Submit for Review", type="primary"):
    if not uploaded_file and not paper_text.strip():
        st.error("Please upload a file or provide text.")
    else:
        with st.spinner("Review in progress..."):
            try:
                if uploaded_file:
                    temp_path = Path("uploads") / uploaded_file.name
                    temp_path.parent.mkdir(exist_ok=True)
                    temp_path.write_bytes(uploaded_file.getvalue())
                    doc = ingestor.ingest(temp_path)
                    result = engine.review_paper(doc)
                else:
                    result = engine.review_paper(paper_text)

                name = paper_name or uploaded_file.name or "submission"
                report_path = report_generator.save_markdown(name, result)

                st.success("Review Complete!")
                st.balloons()

                # Quick verdict
                verdict = result["final_verdict"]
                st.metric("Trust Score", f"{verdict['overall_trust_score']:.3f}")
                st.write(f"**Verdict**: {verdict['verdict_label']}")

                # Full report
                report_md = Path("reports") / report_path.name
                if report_md.exists():
                    st.markdown(report_md.read_text(encoding="utf-8"))
                    with open(report_md, "rb") as f:
                        st.download_button("Download Report", f, file_name=report_path.name)
            except Exception as e:
                st.error(f"Error: {e}")