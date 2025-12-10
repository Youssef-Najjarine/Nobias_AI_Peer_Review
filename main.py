# main.py

from pathlib import Path

from Core.review_engine import ReviewEngine
from Core.report_generator import ReportGenerator
from Utils.file_loader import load_paper


def review_single_paper(paper_path: str, report_generator: ReportGenerator):
    print("=" * 80)
    print(f"Reviewing: {paper_path}")
    print("=" * 80)

    try:
        paper_text = load_paper(paper_path)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return

    engine = ReviewEngine()
    result = engine.review_paper(paper_text)

    # --- Console summary (quick view) ---
    print("\n=== INTEGRITY RESULT ===")
    print(result["integrity"])

    print("\n=== BIAS RESULT (summary) ===")
    print(f"Overall bias score: {result['bias']['overall_bias_score']:.4f}")

    stats = result["statistics"]
    print("\n=== STATISTICAL RESULT (summary) ===")
    print(f"Has statistical content: {stats['has_statistical_content']}")
    print(f"P-value count: {stats['p_values']['count']}")
    print(f"Rigor score: {stats['overall_rigor_score']:.4f}")

    meth = result["methodology"]
    print("\n=== METHODOLOGY RESULT (summary) ===")
    print(f"Methodology score: {meth['overall_methodology_score']:.4f}")
    print("Sample sizes:", meth["sample_size"]["values"])
    print("Has control group:", meth["control_and_blinding"]["has_control_group"])
    print("Has randomization:", meth["design"]["has_randomization"])
    print("Has preregistration:", meth["transparency"]["has_preregistration"])
    print("Has data sharing:", meth["transparency"]["has_data_sharing"])

    print("\n=== REASONING TRACE (first few steps) ===")
    for step in result["trace"][:5]:
        print(f"[{step['timestamp']}] {step['tag']}: {step['description']}")
        if step.get("metadata"):
            print("  metadata:", step["metadata"])

    # --- Report output ---
    paper_name = Path(paper_path).stem  # e.g. "astrophysics_example"
    report_path = report_generator.save_markdown(paper_name, result)
    print(f"\nReport saved to: {report_path}\n")


def main():
    # List of your PDF filenames in the project root
    paper_files = [
        "astrophysics_example.pdf",
        "medical_example.pdf",
        "psychology_example.pdf",
        "social_science_example.pdf",
    ]

    report_generator = ReportGenerator()

    for paper in paper_files:
        review_single_paper(paper, report_generator)


if __name__ == "__main__":
    main()
