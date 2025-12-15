# main.py
from __future__ import annotations

from pathlib import Path

from Core.ingestion import DocumentIngestor
from Core.review_engine import ReviewEngine
from Core.report_generator import ReportGenerator


def review_single_paper(
    paper_path: Path,
    engine: ReviewEngine,
    report_generator: ReportGenerator,
    ingestor: DocumentIngestor,
) -> None:
    print("=" * 80)
    print(f"Reviewing: {paper_path.name}")
    print("=" * 80)

    # --- Ingestion ---
    doc = ingestor.ingest(paper_path)

    # --- Ingestion metadata (debug-friendly, minimal) ---
    print(
        f"[Ingestion] "
        f"type={doc.doc_type} | "
        f"size={doc.byte_size:,} bytes | "
        f"raw_chars={len(doc.raw_text):,} | "
        f"clean_chars={len(doc.clean_text):,} | "
        f"sections={len(doc.sections)}"
    )

    # --- Review (use clean_text for analysis) ---
    result = engine.review_paper(doc)

    integrity = result["integrity"]
    bias = result["bias"]
    stats = result["statistics"]
    meth = result["methodology"]
    replication = result["replication"]  # Option A schema

    # --- Integrity summary ---
    print("\n=== INTEGRITY RESULT ===")
    print(
        {
            "is_empty": integrity["is_empty"],
            "word_count": integrity["word_count"],
            "passes_minimum_length": integrity["passes_minimum_length"],
        }
    )

    # --- Bias summary ---
    print("\n=== BIAS RESULT (summary) ===")
    print(f"Overall bias score: {bias['overall_bias_score']:.4f}")

    # --- Statistics summary ---
    print("\n=== STATISTICAL RESULT (summary) ===")
    print(f"Has statistical content: {stats['has_statistical_content']}")
    print(f"P-value count: {stats['p_values']['count']}")
    print(f"Rigor score: {stats['overall_rigor_score']:.4f}")

    # --- Methodology summary ---
    sample_sizes = meth["sample_size"]["values"]
    print("\n=== METHODOLOGY RESULT (summary) ===")
    print(f"Methodology score: {meth['overall_methodology_score']:.4f}")
    print(f"Sample sizes: {sample_sizes}")
    print(f"Has control group: {meth['control_and_blinding']['has_control_group']}")
    print(f"Has randomization: {meth['design']['has_randomization']}")
    print(f"Has preregistration: {meth['transparency']['has_preregistration']}")
    print(f"Has data sharing: {meth['transparency']['has_data_sharing']}")

    # --- Replication summary (Option A) ---
    replication_score = replication["overall_replicability_score"]
    simulated_outcome = replication["simulated_replication_outcome"]
    claims = replication["claims"]
    robustness = replication["robustness"]
    openness = replication["openness"]

    print("\n=== REPLICATION RESULT (summary) ===")
    print(f"Replicability score: {replication_score:.4f}")
    print(f"Simulated outcome: {simulated_outcome}")
    print(f"Has replication claims: {claims['has_replication_claims']}")
    print(
        "Robustness signals:",
        {
            "bootstrap": robustness["mentions_bootstrap"],
            "monte_carlo": robustness["mentions_monte_carlo"],
            "sensitivity_analysis": robustness["mentions_sensitivity_analysis"],
        },
    )
    print(
        "Openness signals:",
        {
            "open_data": openness["has_open_data"],
            "open_code": openness["has_open_code"],
            "preregistration": openness["has_preregistration"],
        },
    )

    # --- Reasoning trace preview ---
    print("\n=== REASONING TRACE (first few steps) ===")
    for step in result["trace"][:5]:
        print(f"[{step['timestamp']}] {step['tag']}: {step['description']}")
        if step.get("metadata"):
            print(f"  metadata: {step['metadata']}")

    # --- Report write-out ---
    report_path = report_generator.save_markdown(paper_path.stem, result)
    print(f"\nReport saved to: {report_path}\n")


def main() -> None:
    project_root = Path(__file__).resolve().parent
    papers_dir = project_root / "papers"

    paper_files = [
        "astrophysics_example.pdf",
        "medical_example.pdf",
        "psychology_example.pdf",
        "social_science_example.pdf",
        "Prometheus_Prime_Paper_1.pdf",
    ]

    engine = ReviewEngine()
    report_generator = ReportGenerator()
    ingestor = DocumentIngestor()

    for paper_name in paper_files:
        pdf_path = papers_dir / paper_name
        review_single_paper(pdf_path, engine, report_generator, ingestor)


if __name__ == "__main__":
    main()
