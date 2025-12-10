# Core/plagiarism_checker.py

import re
from collections import Counter
from typing import Dict, Any, List


class PlagiarismChecker:
    """
    Heuristic internal plagiarism / redundancy detector.

    This does NOT claim legal plagiarism, but flags patterns like:
      - heavy reuse of the same 5-gram phrases
      - repeated sentences
      - low unique-phrase ratio (high compressibility)

    It produces a bounded suspicion score in [0, 1].
    """

    def _normalize_tokens(self, text: str) -> List[str]:
        # Lowercase and keep only alphanumeric-ish tokens
        tokens = re.findall(r"[A-Za-z0-9']+", text.lower())
        return tokens

    def _split_sentences(self, text: str) -> List[str]:
        # Very crude sentence splitter
        raw = re.split(r"[.!?]+", text)
        sentences = []
        for s in raw:
            s_norm = re.sub(r"\s+", " ", s.strip())
            if len(s_norm) > 0:
                sentences.append(s_norm)
        return sentences

    def _ngram_stats(self, tokens: List[str], n: int = 5) -> Dict[str, Any]:
        if len(tokens) < n:
            return {
                "total": 0,
                "unique": 0,
                "max_freq": 0,
                "top": [],
            }

        ngrams = [
            " ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)
        ]
        counts = Counter(ngrams)
        total = len(ngrams)
        unique = len(counts)
        max_freq = max(counts.values()) if counts else 0

        top = [ng for ng, _ in counts.most_common(5)]

        return {
            "total": total,
            "unique": unique,
            "max_freq": max_freq,
            "top": top,
        }

    def _sentence_redundancy(self, sentences: List[str]) -> Dict[str, Any]:
        if not sentences:
            return {
                "repeated_ratio": 0.0,
                "top_repeated": [],
            }

        counts = Counter(sentences)
        repeated = [s for s, c in counts.items() if c > 1]
        repeated_occurrences = sum(c for s, c in counts.items() if c > 1)
        total = len(sentences)

        repeated_ratio = repeated_occurrences / total if total > 0 else 0.0
        top_repeated = [s for s, c in counts.most_common(5) if c > 1]

        return {
            "repeated_ratio": repeated_ratio,
            "top_repeated": top_repeated,
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze redundancy / reuse patterns and return:

            - ngram_repetition_ratio
            - highest_ngram_frequency
            - top_repeated_ngrams
            - repeated_sentence_ratio
            - top_repeated_sentences
            - overall_plagiarism_suspicion_score (0-1)
        """
        if not text.strip():
            return {
                "ngram_repetition_ratio": 0.0,
                "highest_ngram_frequency": 0,
                "top_repeated_ngrams": [],
                "repeated_sentence_ratio": 0.0,
                "top_repeated_sentences": [],
                "overall_plagiarism_suspicion_score": 0.0,
            }

        tokens = self._normalize_tokens(text)
        sentences = self._split_sentences(text)

        ngram_info = self._ngram_stats(tokens, n=5)
        sent_info = self._sentence_redundancy(sentences)

        total_ngrams = ngram_info["total"]
        unique_ngrams = ngram_info["unique"]

        if total_ngrams > 0:
            # 1 - (unique/total) → higher means more repetition
            ngram_repetition_ratio = 1.0 - (unique_ngrams / total_ngrams)
        else:
            ngram_repetition_ratio = 0.0

        repeated_sentence_ratio = sent_info["repeated_ratio"]
        highest_ngram_frequency = ngram_info["max_freq"]

        # ------------------------------------------------------------------
        # Scoring heuristic
        # ------------------------------------------------------------------
        # Base from n-gram repetition (0-0.7 weight)
        base_score = min(0.7, ngram_repetition_ratio * 0.7 * 2.0)

        # Extra bump if many sentences are repeated (0-0.2)
        sentence_component = min(0.2, repeated_sentence_ratio * 0.4)

        # Extra bump if some 5-gram appears a lot (0-0.1)
        frequency_component = 0.0
        if highest_ngram_frequency >= 8:
            frequency_component = 0.1
        elif highest_ngram_frequency >= 5:
            frequency_component = 0.05

        overall = base_score + sentence_component + frequency_component
        overall = max(0.0, min(1.0, overall))

        return {
            "ngram_repetition_ratio": ngram_repetition_ratio,
            "highest_ngram_frequency": highest_ngram_frequency,
            "top_repeated_ngrams": ngram_info["top"],
            "repeated_sentence_ratio": repeated_sentence_ratio,
            "top_repeated_sentences": sent_info["top_repeated"],
            "overall_plagiarism_suspicion_score": overall,
        }
