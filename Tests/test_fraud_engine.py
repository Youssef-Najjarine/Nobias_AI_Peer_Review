# Tests/test_fraud_engine.py

from Core.fraud_detector import FraudDetector


def test_fraud_detector_scores_in_range():
    """
    Basic sanity: fraud detector should always return a suspiciousness_score
    between 0 and 1.
    """
    detector = FraudDetector()

    text = """
    The study reports several results but openly shares raw data and analysis code.
    There is no indication of selective reporting or data fabrication.
    """

    result = detector.analyze_fraud(text)

    assert "suspiciousness_score" in result
    score = result["suspiciousness_score"]
    assert 0.0 <= score <= 1.0


def test_fraud_detector_flags_suspicious_pattern():
    """
    A text with obviously sketchy patterns (identical p-values,
    refusal to share data, etc.) should get a higher suspiciousness score
    than a clean, transparent description.
    """
    detector = FraudDetector()

    clean_text = """
    We preregistered all hypotheses, share raw data and analysis scripts,
    and report all outcomes, including non-significant results.
    """

    sketchy_text = """
    All 37 tests yielded p = 0.049 exactly, with identical means across conditions.
    We do not share raw data or code due to proprietary concerns.
    Some observations were manually adjusted to better reflect the theory.
    """

    clean_result = detector.analyze_fraud(clean_text)
    sketchy_result = detector.analyze_fraud(sketchy_text)

    clean_score = clean_result["suspiciousness_score"]
    sketchy_score = sketchy_result["suspiciousness_score"]

    assert 0.0 <= clean_score <= 1.0
    assert 0.0 <= sketchy_score <= 1.0

    # The obviously sketchy description should look worse than the clean one.
    assert sketchy_score >= clean_score
