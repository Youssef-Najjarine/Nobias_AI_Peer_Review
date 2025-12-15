# Ai_Models/reviewer_llm.py
from __future__ import annotations

from typing import Dict, Any, List

class ReviewerLLMStub:
    """
    Stub for future symbolic reviewer model.
    Currently returns deterministic, rule-based feedback.
    """
    def generate_review_comment(self, section: str, content: str) -> str:
        if "p < 0.05" in content and "multiple" in content.lower():
            return "Consider correcting for multiple comparisons."
        if "n = " in content and int(content.split("n = ")[-1].split()[0]) < 30:
            return "Sample size appears small — check statistical power."
        return "No specific concerns detected in this section."

    def batch_review(self, paper_sections: Dict[str, str]) -> List[Dict[str, Any]]:
        comments = []
        for section, text in paper_sections.items():
            comment = self.generate_review_comment(section, text)
            if comment != "No specific concerns detected in this section.":
                comments.append({
                    "section": section,
                    "comment": comment,
                    "severity": "medium",
                })
        return comments