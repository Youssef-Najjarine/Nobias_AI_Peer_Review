# Ai_Models/hallucination_detector.py
from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, Any, List


class HallucinationDetector:
    """
    Deterministic, transparent self-audit engine.
    Detects overconfident claims, contradictions, and evidence misalignment
    without any external LLM — pure rules and heuristics for full auditability.
    """

    # Patterns that demand strong evidence
    HIGH_RISK_CLAIMS = [
        r"\bproven?\b",
        r"\bestablished fact\b",
        r"\bdefinitive\b",
        r"\birrefutable\b",
        r"\bobviously\b",
        r"\bclearly\b",
        r"\bwithout doubt\b",
        r"\bunanimous consensus\b",
        r"\ball experts agree\b",
        r"\bno serious scientist disputes\b",
    ]

    # Potential logical contradictions
    CONTRADICTION_PATTERNS = [
        r"however.*not significant",
        r"significant.*however.*no effect",
        r"strong evidence.*cannot conclude",
        r"results show.*but we reject",
        r"supports? the hypothesis.*fails? to reach significance",
    ]

    def __init__(self) -> None:
        self.compiled_high_risk = [re.compile(p, re.IGNORECASE) for p in self.HIGH_RISK_CLAIMS]
        self.compiled_contradictions = [re.compile(p, re.IGNORECASE) for p in self.CONTRADICTION_PATTERNS]

    def detect_high_risk_claims(self, text: str) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for pattern in self.compiled_high_risk:
            for match in pattern.finditer(text):
                context = text[max(0, match.start() - 60):match.end() + 60]
                findings.append({
                    "type": "high_risk_claim",
                    "match": match.group(0),
                    "context": context.strip(),
                    "severity": "high",
                    "recommendation": "Requires direct empirical backing or citation",
                })
        return findings

    def detect_contradictions(self, text: str) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        lowered = text.lower()
        for pattern in self.compiled_contradictions:
            for match in pattern.finditer(lowered):
                start = max(0, match.start() - 100)
                end = match.end() + 100
                context = text[start:end]
                findings.append({
                    "type": "potential_contradiction",
                    "match": match.group(0),
                    "context": context.strip(),
                    "severity": "medium",
                    "recommendation": "Verify logical consistency between claim and evidence",
                })
        return findings

    def check_evidence_alignment(self, claim_text: str, supporting_text: str) -> Dict[str, Any]:
        """Lightweight check: does supporting text contain quantitative signals?"""
        has_numbers = bool(re.search(r"\d", supporting_text))
        has_p_value = bool(re.search(r"p\s*[<=>]", supporting_text, re.IGNORECASE))
        has_effect = bool(re.search(r"effect|correlation|difference|regression", supporting_text, re.IGNORECASE))

        evidence_strength = sum([has_numbers, has_p_value, has_effect])

        return {
            "evidence_aligned": evidence_strength >= 2,
            "evidence_signals": {
                "has_numbers": has_numbers,
                "has_p_value": has_p_value,
                "has_effect_term": has_effect,
            },
            "alignment_score": evidence_strength / 3.0,
        }

    def audit_module(self, module_name: str, output: Dict[str, Any], source_text: str) -> Dict[str, Any]:
        """
        Full self-audit of a single module's output.
        """
        audit_time = datetime.utcnow().isoformat()

        # Collect any textual claims from the output
        claim_texts: List[str] = []
        if isinstance(output.get("reasons"), list):
            claim_texts.extend(output["reasons"])
        if isinstance(output.get("summary"), str):
            claim_texts.append(output["summary"])
        if isinstance(output.get("findings"), list):
            claim_texts.extend(str(f) for f in output["findings"])

        text_to_audit = " ".join(claim_texts)

        findings = []
        findings.extend(self.detect_high_risk_claims(text_to_audit))
        findings.extend(self.detect_contradictions(text_to_audit))

        high_count = sum(1 for f in findings if f["severity"] == "high")
        total_findings = len(findings)

        risk_score = min(1.0, (high_count * 0.4) + (total_findings * 0.08))

        return {
            "module": module_name,
            "audit_time": audit_time,
            "hallucination_risk_score": round(risk_score, 4),
            "findings_count": total_findings,
            "high_severity_count": high_count,
            "findings": findings,
            "passed_self_audit": risk_score < 0.25,
            "summary": f"{total_findings} potential issues ({high_count} high-severity)",
        }