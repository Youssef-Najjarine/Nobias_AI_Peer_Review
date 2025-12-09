# Core/bias_detector.py

import re
from collections import Counter
from typing import List, Dict


class BiasDetector:
    """
    Lightweight, rule-based bias detector.
    This does NOT try to be 'AI smart' yet – it's a transparent,
    auditable first-pass signal generator.
    """

    def __init__(self) -> None:
        # You can expand/tune these lists over time.
        self.emotional_words = {
            "outrageous", "shocking", "alarming", "unprecedented",
            "remarkable", "astonishing", "incredible", "dramatic",
            "catastrophic", "revolutionary", "groundbreaking",
        }

        self.authority_terms = {
            "famous", "renowned", "leading", "prestigious",
            "top", "world-class", "celebrated", "influential",
            "nobel", "ivy-league",
        }

        self.ideological_terms = {
            "ideology", "dogma", "orthodox", "heretical",
            "mainstream", "fringe", "consensus", "denier",
        }

        self.affiliation_markers = {
            "elite", "institution", "ivy", "industry-funded",
            "independent", "grassroots",
        }

        self.certainty_words = {
            "obviously", "clearly", "undeniably", "certainly",
            "without doubt", "beyond doubt", "conclusively",
        }

    # ---------- Public API ----------

    def analyze_text(self, text: str) -> Dict:
        """
        Main entry point.
        Returns a dictionary with bias-related metrics.
        """
        tokens = self._tokenize(text)
        total_words = max(len(tokens), 1)  # avoid divide-by-zero

        emotional = self._find_matches(tokens, self.emotional_words)
        authority = self._find_matches(tokens, self.authority_terms)
        ideological = self._find_matches(tokens, self.ideological_terms)
        affiliation = self._find_matches(tokens, self.affiliation_markers)
        certainty = self._find_matches(tokens, self.certainty_words)

        # Simple density metrics
        emotional_density = emotional["count"] / total_words
        authority_density = authority["count"] / total_words
        ideological_density = ideological["count"] / total_words
        affiliation_density = affiliation["count"] / total_words
        certainty_density = certainty["count"] / total_words

        # Naive overall score: weighted sum, capped at 1.0
        overall_score = min(
            emotional_density * 3.0
            + authority_density * 2.0
            + ideological_density * 2.0
            + affiliation_density * 1.5
            + certainty_density * 2.5,
            1.0,
        )

        return {
            "total_words": total_words,
            "emotional_language": {
                "count": emotional["count"],
                "density": emotional_density,
                "examples": emotional["examples"],
            },
            "authority_appeals": {
                "count": authority["count"],
                "density": authority_density,
                "examples": authority["examples"],
            },
            "ideological_language": {
                "count": ideological["count"],
                "density": ideological_density,
                "examples": ideological["examples"],
            },
            "affiliation_bias_markers": {
                "count": affiliation["count"],
                "density": affiliation_density,
                "examples": affiliation["examples"],
            },
            "certainty_language": {
                "count": certainty["count"],
                "density": certainty_density,
                "examples": certainty["examples"],
            },
            "overall_bias_score": overall_score,
        }

    # ---------- Internal helpers ----------

    def _tokenize(self, text: str) -> List[str]:
        """
        Very simple tokenizer: lowercase + split on non-letters.
        This keeps the logic transparent and dependency-free.
        """
        text = text.lower()
        return re.findall(r"[a-z']+", text)

    def _find_matches(self, tokens: List[str], vocab: set) -> Dict:
        """
        Count and collect example matches between tokens and a vocabulary set.
        """
        matches = [t for t in tokens if t in vocab]
        counter = Counter(matches)
        # Keep up to 10 most common examples to avoid huge payloads
        examples = [w for w, _ in counter.most_common(10)]

        return {
            "count": len(matches),
            "examples": examples,
        }
