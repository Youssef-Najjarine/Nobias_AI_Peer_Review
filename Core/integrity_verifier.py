# Core/integrity_verifier.py
import re
from typing import Dict

from Utils.math_utils import MathDetector


class IntegrityVerifier:
    """
    Expanded integrity checker: length, structure, math density, self-consistency signals.
    """
    def __init__(self):
        self.math_detector = MathDetector()

    def check_basic_integrity(self, paper_text: str) -> Dict:
        stripped = paper_text.strip()
        word_count = len(stripped.split()) if stripped else 0
        char_count = len(stripped)
        has_sections = bool(re.search(r"introduction|methods|results|discussion|conclusion", stripped, re.IGNORECASE))
        math_analysis = self.math_detector.analyze(paper_text)

        return {
            "is_empty": word_count == 0,
            "word_count": word_count,
            "char_count": char_count,
            "passes_minimum_length": word_count >= 500,  # Raised threshold for real papers
            "has_academic_sections": has_sections,
            "math_analysis": math_analysis,
            "overall_integrity_score": min(1.0, 
                (word_count / 3000.0) + 
                (0.3 if has_sections else 0) + 
                math_analysis["math_density_score"] * 0.2
            ),
        }