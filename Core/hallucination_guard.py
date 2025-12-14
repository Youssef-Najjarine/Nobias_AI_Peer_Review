# Core/hallucination_guard.py
from __future__ import annotations

from typing import Dict, Any, List

from Ai_Models.hallucination_detector import HallucinationDetector


class HallucinationGuard:
    """
    Integrates the HallucinationDetector into the review pipeline.
    Audits key modules and attaches results to the reasoning trace.
    """

    def __init__(self) -> None:
        self.detector = HallucinationDetector()
        self.audit_history: List[Dict[str, Any]] = []

    def audit(self, module_name: str, result: Dict[str, Any], paper_text: str) -> Dict[str, Any]:
        audit_result = self.detector.audit_module(module_name, result, paper_text)
        self.audit_history.append(audit_result)
        return audit_result

    def get_overall_audit(self) -> Dict[str, Any]:
        if not self.audit_history:
            return {"overall_hallucination_risk": 0.0, "total_findings": 0, "passed_all": True}

        risks = [a["hallucination_risk_score"] for a in self.audit_history]
        total_findings = sum(a["findings_count"] for a in self.audit_history)
        passed_all = all(a["passed_self_audit"] for a in self.audit_history)

        return {
            "overall_hallucination_risk": round(max(risks or [0.0]), 4),
            "total_findings": total_findings,
            "passed_all_audits": passed_all,
            "module_count": len(self.audit_history),
        }