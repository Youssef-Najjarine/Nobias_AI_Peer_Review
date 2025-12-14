# Utils/nlp_utils.py
import re
from typing import List, Tuple


def sent_tokenize(text: str) -> List[str]:
    """
    Lightweight sentence tokenizer (no external deps).
    Better than split('.') for scientific text.
    """
    if not text.strip():
        return []

    # Split on .!? followed by space and capital letter, or paragraph
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])|(?<=\n\n)(?=[A-Z])', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def word_tokenize(text: str) -> List[str]:
    """
    Simple word tokenizer preserving scientific terms.
    """
    return re.findall(r"[a-zA-Z]+(?:['-][a-zA-Z]+)*|\d+(?:\.\d+)?|[^\s\w]", text)


def ngrams(tokens: List[str], n: int = 2) -> List[Tuple[str, ...]]:
    """
    Generate n-grams from token list.
    """
    if len(tokens) < n:
        return []
    # Explicit loop to avoid zip type checker warning
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]