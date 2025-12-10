# Tests/test_review_flow.py

from Core.review_engine import ReviewEngine


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
    assert "trace" in result

    integrity = result["integrity"]
    bias = result["bias"]
    stats = result["statistics"]
    meth = result["methodology"]

    # Integrity should see non-empty text and some positive word count
    assert integrity["is_empty"] is False
    assert integrity["word_count"] > 0

    # Bias score should be between 0 and 1
    assert 0.0 <= bias["overall_bias_score"] <= 1.0

    # Statistical rigor score should be between 0 and 1
    assert 0.0 <= stats["overall_rigor_score"] <= 1.0
    # In this specific sample, we expect some statistical content
    assert stats["has_statistical_content"] is True
    assert stats["p_values"]["count"] >= 1

    # Methodology score should be between 0 and 1
    assert 0.0 <= meth["overall_methodology_score"] <= 1.0
    # We expect at least one sample size detected
    assert meth["sample_size"]["count"] >= 1
    # We expect randomization and a control group from this text
    assert meth["design"]["has_randomization"] is True
    assert meth["control_and_blinding"]["has_control_group"] is True


def test_review_flow_with_empty_text():
    """
    Edge case: empty or whitespace-only text.
    Ensures the engine doesn't crash and flags the text as empty.
    """
    engine = ReviewEngine()
    result = engine.review_paper("   \n  ")

    integrity = result["integrity"]
    stats = result["statistics"]
    meth = result["methodology"]

    # Integrity: should mark as empty and have zero words
    assert integrity["is_empty"] is True
    assert integrity["word_count"] == 0

    # Stats: no statistical content
    assert stats["has_statistical_content"] is False
    assert stats["p_values"]["count"] == 0

    # Methodology: no sample sizes
    assert meth["sample_size"]["count"] == 0

def test_methodology_rescues_stats_when_sample_sizes_present():
    """
    If no explicit stats are detected but sample sizes are present,
    stats.has_statistical_content should be True and rigor >= 0.25
    due to the cross-wiring logic.
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

    # Methodology should see at least one sample size
    assert meth["sample_size"]["count"] >= 1

    # Even with no p-values, stats should be treated as present
    assert stats["has_statistical_content"] is True
    assert stats["p_values"]["count"] == 0
    assert stats["overall_rigor_score"] >= 0.25
