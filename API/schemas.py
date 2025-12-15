# API/schemas.py
from pydantic import BaseModel
from typing import Any, Dict, List

class VerdictSummary(BaseModel):
    overall_trust_score: float
    verdict_label: str
    reasons: List[str]

class HallucinationSummary(BaseModel):
    overall_hallucination_risk: float
    passed_all_audits: bool
    total_findings: int

class ReviewResponse(BaseModel):
    paper_name: str
    status: str
    final_verdict: VerdictSummary
    hallucination_audit: HallucinationSummary
    report_url: str
    full_result: Dict[str, Any] | None = None  # Optional in prod