# Core/ethics_guard.py

import re
from typing import Dict, Any, List


class EthicsGuard:
    """
    Heuristic ethics & safety analyzer.

    This is NOT a legal or regulatory decision engine.
    It just flags:
      - likely human-subject research
      - presence/absence of ethics approval mention
      - informed consent & data protection signals
      - vulnerable populations
      - high-risk / dual-use terms

    Output:
      - has_human_subjects: bool
      - has_vulnerable_population: bool
      - has_ethics_approval_mention: bool
      - has_informed_consent_mention: bool
      - mentions_data_protection: bool
      - risk_terms: {count, examples}
      - overall_ethics_risk_score in [0, 1] (0 = low risk, 1 = high risk)
    """

    HUMAN_SUBJECT_TERMS = [
        "participant",
        "participants",
        "subject",
        "subjects",
        "patient",
        "patients",
        "respondent",
        "respondents",
        "interviewee",
        "interviewees",
        "survey",
        "surveys",
        "questionnaire",
        "human trial",
        "clinical trial",
        "human subjects",
    ]

    VULNERABLE_TERMS = [
        "children",
        "minors",
        "adolescents",
        "pregnant women",
        "prisoners",
        "incarcerated",
        "inmates",
        "vulnerable population",
        "cognitively impaired",
        "mentally impaired",
        "elderly",
        "dementia",
    ]

    ETHICS_APPROVAL_TERMS = [
        "institutional review board",
        "irb",
        "ethics committee",
        "ethics board",
        "research ethics committee",
        "approved by the irb",
        "irb approval",
        "ethics approval",
        "ethical approval",
    ]

    CONSENT_TERMS = [
        "informed consent",
        "written consent",
        "verbal consent",
        "consent was obtained",
        "participants provided consent",
        "parental consent",
        "assent and consent",
    ]

    DATA_PROTECTION_TERMS = [
        "gdpr",
        "hipaa",
        "anonymized",
        "de-identified",
        "pseudonymized",
        "data protection",
        "confidentiality",
        "secure storage",
        "encrypted",
        "privacy-preserving",
    ]

    HIGH_RISK_TERMS = [
        "gain of function",
        "bioweapon",
        "bioterror",
        "weaponized",
        "dual-use",
        "dual use",
        "pathogen release",
        "pandemic potential",
        "lethal dose",
        "cds in vivo gene editing",
        "crispr",
        "germline editing",
        "human challenge trial",
        "challenge study",
    ]

    def _contains_any(self, text_lower: str, terms: List[str]) -> bool:
        return any(term in text_lower for term in terms)

    def _collect_terms(self, text_lower: str, terms: List[str]) -> Dict[str, Any]:
        examples: List[str] = []
        count = 0
        for term in terms:
            if term in text_lower:
                occurrences = text_lower.count(term)
                count += occurrences
                if len(examples) < 5:
                    examples.append(term)
        return {"count": count, "examples": examples}

    def analyze(self, text: str) -> Dict[str, Any]:
        if not text.strip():
            # Completely empty / whitespace -> no signal, zero risk.
            return {
                "has_human_subjects": False,
                "has_vulnerable_population": False,
                "has_ethics_approval_mention": False,
                "has_informed_consent_mention": False,
                "mentions_data_protection": False,
                "risk_terms": {"count": 0, "examples": []},
                "overall_ethics_risk_score": 0.0,
            }

        lowered = text.lower()

        has_human_subjects = self._contains_any(lowered, self.HUMAN_SUBJECT_TERMS)
        has_vulnerable = self._contains_any(lowered, self.VULNERABLE_TERMS)
        has_ethics_approval = self._contains_any(lowered, self.ETHICS_APPROVAL_TERMS)
        has_consent = self._contains_any(lowered, self.CONSENT_TERMS)
        has_data_protection = self._contains_any(lowered, self.DATA_PROTECTION_TERMS)
        risk_info = self._collect_terms(lowered, self.HIGH_RISK_TERMS)

        # ----------------------------------------------------------
        # Scoring heuristic (bounded [0, 1], higher = more risk)
        # ----------------------------------------------------------
        score = 0.0

        # Base risk for human subjects without ethics approval
        if has_human_subjects:
            if not has_ethics_approval:
                score += 0.3
            if not has_consent:
                score += 0.2

        # Extra risk if vulnerable population without explicit consent/approval
        if has_vulnerable:
            score += 0.2
            if not has_ethics_approval or not has_consent:
                score += 0.1

        # High-risk / dual-use terms
        score += min(0.3, 0.05 * risk_info["count"])

        # Data protection mitigates some risk
        if has_data_protection:
            score -= 0.1

        score = max(0.0, min(1.0, score))

        return {
            "has_human_subjects": has_human_subjects,
            "has_vulnerable_population": has_vulnerable,
            "has_ethics_approval_mention": has_ethics_approval,
            "has_informed_consent_mention": has_consent,
            "mentions_data_protection": has_data_protection,
            "risk_terms": risk_info,
            "overall_ethics_risk_score": score,
        }
