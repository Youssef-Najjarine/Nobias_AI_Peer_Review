# Core/ingestion/text_cleaner.py

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CleanedText:
    raw_text: str
    clean_text: str


class TextCleaner:
    """
    Light, conservative cleaning for extracted PDF text.

    Goals:
      - normalize newlines
      - remove common PDF artifacts (hyphenated line-breaks, excessive whitespace)
      - keep content intact (avoid aggressive rewriting)
    """

    _HYPHEN_LINEBREAK_RE = re.compile(r"(\w)-\n(\w)")
    _MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
    _MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

    @staticmethod
    def clean(raw_text: str) -> CleanedText:
        text = raw_text or ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Fix hyphenation across line breaks: "inter-\national" -> "international"
        text = TextCleaner._HYPHEN_LINEBREAK_RE.sub(r"\1\2", text)

        # Collapse excessive spaces/tabs
        text = TextCleaner._MULTI_SPACE_RE.sub(" ", text)

        # Trim trailing spaces per line (helps section heading detection)
        text = "\n".join(line.rstrip() for line in text.split("\n"))

        # Collapse excessive blank lines
        text = TextCleaner._MULTI_NEWLINE_RE.sub("\n\n", text)

        # Final trim
        cleaned = text.strip()

        return CleanedText(raw_text=raw_text or "", clean_text=cleaned)
