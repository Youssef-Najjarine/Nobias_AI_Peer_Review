# Tests/test_review_flow.py
from pathlib import Path
from Core.review_engine import ReviewEngine
from Core.report_generator import ReportGenerator


def test_review_flow_with_nonempty_text():
    """
    Full pipeline sanity test on a non-trivial sample text.
    Ensures all submodules return sane, bounded values.
    """
    sample_text = """
    This groundbreaking and unprecedented study clearly proves our theory.
    The renowned and prestigious group behind this work comes from elite institutions.
    It is obvious that the results are robust.
    We conducted a randomized controlled experiment with a treatment and control group.
    Participants were randomly assigned to conditions and the study was double-blind.
    The sample size was n = 120 in the treatment group and n = 118 in the control group.
    We conducted a series of t-tests and a one-way ANOVA.
    The main effect was significant (p < 0.01), with several follow-up tests
    also significant (p = 0.032, p <= 0.045).
    A 95% CI [1.2, 2.3] was computed for the primary effect size.
    We additionally report Cohen's d as a standardized effect size and
    performed a power analysis to confirm adequate statistical power.
    The protocol was preregistered on OSF.io and the anonymized data
    are available in a public repository.
    """
    engine = ReviewEngine()
    result = engine.review_paper(sample_text)

    # Basic structure checks
    assert "integrity" in result
    assert "bias" in result
    assert "statistics" in result
    assert "methodology" in result
    assert "citations" in result
    assert "plagiarism" in result
    assert "fraud" in result
    assert "ethics" in result
    assert "replication" in result
    assert "hallucination_audit" in result
    assert "trace" in result
    assert "final_verdict" in result

    integrity = result["integrity"]
    bias = result["bias"]
    stats = result["statistics"]
    meth = result["methodology"]
    citations = result["citations"]
    plag = result["plagiarism"]
    fraud = result["fraud"]
    ethics = result["ethics"]
    replication = result["replication"]
    final_verdict = result["final_verdict"]

    # Integrity
    assert integrity["is_empty"] is False
    assert integrity["word_count"] > 0

    # Bias
    assert 0.0 <= bias["overall_bias_score"] <= 1.0

    # Statistics
    assert 0.0 <= stats["overall_rigor_score"] <= 1.0
    assert stats["has_statistical_content"] is True
    assert stats["p_values"]["count"] >= 1

    # Methodology
    assert 0.0 <= meth["overall_methodology_score"] <= 1.0
    assert meth["sample_size"]["count"] >= 1
    assert meth["design"]["has_randomization"] is True
    assert meth["control_and_blinding"]["has_control_group"] is True

    # Citations
    assert 0.0 <= citations["overall_citation_quality_score"] <= 1.0

    # Plagiarism
    assert 0.0 <= plag["overall_plagiarism_suspicion_score"] <= 1.0

    # Fraud
    assert "overall_fraud_suspicion_score" in fraud
    assert 0.0 <= fraud["overall_fraud_suspicion_score"] <= 1.0

    # Ethics
    assert 0.0 <= ethics["overall_ethics_risk_score"] <= 1.0

    # Replication
    assert 0.0 <= replication["overall_replicability_score"] <= 1.0
    assert replication["simulated_replication_outcome"] in {"likely_replicable", "uncertain", "fragile"}

    # Hallucination Audit
    assert "overall_hallucination_risk" in result["hallucination_audit"]
    assert 0.0 <= result["hallucination_audit"]["overall_hallucination_risk"] <= 1.0

    # Final Verdict with Uncertainty
    assert 0.0 <= final_verdict["overall_trust_score"] <= 1.0
    assert "trust_std_dev" in final_verdict
    assert "trust_95_confidence_interval" in final_verdict
    ci = final_verdict["trust_95_confidence_interval"]
    assert len(ci) == 2
    assert ci[0] <= final_verdict["overall_trust_score"] <= ci[1]


def test_review_flow_with_empty_text():
    """
    Edge case: empty or whitespace-only text.
    """
    engine = ReviewEngine()
    result = engine.review_paper(" \n ")

    integrity = result["integrity"]
    stats = result["statistics"]
    meth = result["methodology"]
    citations = result["citations"]
    plag = result["plagiarism"]
    fraud = result["fraud"]
    ethics = result["ethics"]
    replication = result["replication"]

    assert integrity["is_empty"] is True
    assert integrity["word_count"] == 0

    assert stats["has_statistical_content"] is False
    assert stats["p_values"]["count"] == 0

    assert meth["sample_size"]["count"] == 0

    assert citations["estimated_reference_count"] == 0
    assert citations["doi"]["count"] == 0

    assert plag["overall_plagiarism_suspicion_score"] == 0.0

    assert fraud["overall_fraud_suspicion_score"] == 0.0

    assert ethics["overall_ethics_risk_score"] == 0.0

    assert replication["overall_replicability_score"] == 0.0
    assert replication["simulated_replication_outcome"] == "uncertain"


def test_methodology_rescues_stats_when_sample_sizes_present():
    """
    If no explicit stats but sample sizes present → statistical content rescued.
    """
    sample_text = """
    We conducted a large survey with n = 200 participants in the first wave
    and n = 180 participants in the second wave.
    The study was preregistered on OSF.io and focused on descriptive results.
    No hypothesis tests or p-values are reported here.
    """
    engine = ReviewEngine()
    result = engine.review_paper(sample_text)
    stats = result["statistics"]
    meth = result["methodology"]

    assert meth["sample_size"]["count"] >= 1
    assert stats["has_statistical_content"] is True
    assert stats["p_values"]["count"] == 0
    assert stats["overall_rigor_score"] >= 0.25


def test_report_generator_creates_markdown(tmp_path):
    """
    Ensures report generation works and includes key sections.
    """
    sample_text = """
    This groundbreaking study clearly proves our theory.
    We conducted a randomized experiment with n = 50.
    The main effect was significant (p < 0.01).
    Data available on OSF.io.
    """
    engine = ReviewEngine()
    result = engine.review_paper(sample_text)

    report_generator = ReportGenerator(output_dir=tmp_path)
    paper_name = "unit_test_paper"
    out_path: Path = report_generator.save_markdown(paper_name, result)

    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")

    assert f"# Nobias AI Peer Review – {paper_name}" in content
    assert "## Final Verdict" in content
    assert "## Summary Scores" in content
    assert "## Bias & Language" in content
    assert "## Statistical Rigor" in content
    assert "## Methodology & Design" in content
    assert "## Replicability & Robustness" in content
    assert "## Citations & References" in content
    assert "## Plagiarism / Redundancy Signals" in content
    assert "## Fraud / Anomaly Signals" in content
    assert "## Ethics & Safety" in content
    assert "## Integrity Checks" in content
    assert "## Self-Audit: Hallucination & Overconfidence Check" in content
    assert "## Reasoning Trace (first steps)" in content