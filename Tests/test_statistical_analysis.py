# Tests/test_statistical_analysis.py
from Core.statistical_analyzer import StatisticalAnalyzer

def test_statistical_analyzer_detects_p_values():
    analyzer = StatisticalAnalyzer()
    text = "The effect was significant (p < 0.01) and p = 0.032."
    result = analyzer.analyze(text)

    assert result["has_statistical_content"] is True
    assert result["p_values"]["count"] >= 2

def test_methodology_rescues_stats():
    # Cross-wiring test
    from Core.review_engine import ReviewEngine
    text = "n = 200 participants. No p-values reported."
    engine = ReviewEngine()
    result = engine.review_paper(text)

    assert result["statistics"]["has_statistical_content"] is True
    assert result["statistics"]["overall_rigor_score"] >= 0.25