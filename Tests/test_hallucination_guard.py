# Tests/test_hallucination_guard.py
from Ai_Models.hallucination_detector import HallucinationDetector
from Core.hallucination_guard import HallucinationGuard

def test_hallucination_detector_flags_overconfidence():
    detector = HallucinationDetector()
    text = "This clearly proves that the theory is correct without doubt."
    audit = detector.audit_module("test", {"reasons": [text]}, text)

    assert audit["hallucination_risk_score"] > 0.2
    assert audit["findings_count"] > 0

def test_hallucination_guard_integration():
    guard = HallucinationGuard()
    result = {"reasons": ["This is obviously true."]}
    audit = guard.audit("bias", result, "paper text")

    assert "hallucination_risk_score" in audit
    assert guard.get_overall_audit()["module_count"] == 1