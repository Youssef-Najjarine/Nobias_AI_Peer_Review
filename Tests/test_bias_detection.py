# Tests/test_bias_detection.py
from Core.bias_detector import BiasDetector

def test_bias_detector_identifies_emotional_language():
    detector = BiasDetector()
    text = "This shocking and revolutionary discovery will change everything!"
    result = detector.analyze_text(text)

    assert result["emotional_language"]["count"] > 0
    assert result["overall_bias_score"] > 0.2

def test_bias_detector_clean_text():
    detector = BiasDetector()
    text = "We conducted an experiment with n=100. Results showed p=0.03."
    result = detector.analyze_text(text)

    assert result["overall_bias_score"] < 0.1