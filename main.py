# main.py

from pathlib import Path

from Core.review_engine import ReviewEngine
from Core.report_generator import ReportGenerator
from Utils.file_loader import load_paper


from pathlib import Path

from Core.review_engine import ReviewEngine
from Core.report_generator import ReportGenerator
from Utils.file_loader import load_paper

def review_single_paper(paper_path: Path, report_generator: ReportGenerator) -> None:
    print("=" * 80)
    print(f"Reviewing: {paper_path.name}")
    print("=" * 80)

    # Use the high-level loader that understands PDFs and text
    paper_text = load_paper(str(paper_path))

    engine = ReviewEngine()
    result = engine.review_paper(paper_text)

    integrity = result["integrity"]
    bias = result["bias"]
    stats = result["statistics"]
    meth = result["methodology"]
    replication = result.get("replication")  # may be None if not wired for some reason

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

    # --- Replication summary ---
    if replication is not None:
        score = replication.get("overall_replication_score")
        print("\n=== REPLICATION RESULT (summary) ===")
        if score is not None:
            print(f"Replicability score: {score:.4f}")

        claims = replication.get("claims") or {}
        robustness = replication.get("robustness") or {}
        openness = replication.get("openness") or {}

        if claims:
            print(f"Has replication claims: {claims.get('has_replication_claims', False)}")
        if robustness:
            print(
                "Robustness signals:",
                {
                    "bootstrap": robustness.get("mentions_bootstrap", False),
                    "monte_carlo": robustness.get("mentions_monte_carlo", False),
                    "sensitivity_analysis": robustness.get(
                        "mentions_sensitivity_analysis", False
                    ),
                },
            )
        if openness:
            print(
                "Openness signals:",
                {
                    "open_data": openness.get("has_open_data", False),
                    "open_code": openness.get("has_open_code", False),
                    "prereg": openness.get("has_preregistration", False),
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

def main():
    # Base directory where main.py lives
    base_dir = Path(__file__).parent

    # List of your PDF filenames relative to the project root
    paper_files = [
        "astrophysics_example.pdf",
        "medical_example.pdf",
        "psychology_example.pdf",
        "social_science_example.pdf",
        "Prometheus_Prime_Paper_1.pdf",
    ]

    report_generator = ReportGenerator()

    for paper_name in paper_files:
        pdf_path = base_dir / paper_name
        review_single_paper(pdf_path, report_generator)

if __name__ == "__main__":
    main()
