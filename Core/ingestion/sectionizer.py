from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Section:
    name: str
    start: int
    end: int
    text: str


class Sectionizer:
    """
    Heuristic section splitter for scientific PDFs.

    Output is conservative:
      - If we can't confidently split, we return one section: "full_text"
      - Headings are detected by common academic section names.
    """

    _HEADINGS: tuple[str, ...] = (
        "abstract",
        "introduction",
        "background",
        "related work",
        "methods",
        "method",
        "materials and methods",
        "materials & methods",
        "methodology",
        "experimental setup",
        "experiments",
        "results",
        "analysis",
        "discussion",
        "conclusion",
        "conclusions",
        "limitations",
        "future work",
        "acknowledgments",
        "acknowledgements",
        "references",
        "bibliography",
    )

    def split(self, text: str) -> list[Section]:
        if not text.strip():
            return [Section(name="full_text", start=0, end=0, text="")]

        matches = self._find_heading_matches(text)
        if len(matches) < 2:
            return [Section(name="full_text", start=0, end=len(text), text=text)]

        sections: list[Section] = []
        for i, (name, _start_idx, end_idx) in enumerate(matches):
            section_start = end_idx  # content starts after heading line
            section_end = matches[i + 1][1] if i + 1 < len(matches) else len(text)
            chunk = text[section_start:section_end].strip()

            sections.append(
                Section(
                    name=name,
                    start=section_start,
                    end=section_end,
                    text=chunk,
                )
            )

        if all(not s.text for s in sections):
            return [Section(name="full_text", start=0, end=len(text), text=text)]

        return sections

    def _find_heading_matches(self, text: str) -> list[tuple[str, int, int]]:
        """
        Returns list of tuples:
          (normalized_heading_name, heading_line_start_index, heading_line_end_index)
        """
        results: list[tuple[str, int, int]] = []

        for line_text, start, end in self._iter_lines_with_offsets(text):
            normalized = self._normalize_heading(line_text)
            if normalized is not None:
                results.append((normalized, start, end))

        # Deduplicate consecutive duplicates (e.g., repeated "References")
        deduped: list[tuple[str, int, int]] = []
        for item in results:
            if not deduped or deduped[-1][0] != item[0]:
                deduped.append(item)

        return deduped

    @staticmethod
    def _iter_lines_with_offsets(text: str) -> Iterable[tuple[str, int, int]]:
        start = 0
        for m in re.finditer(r".*?(?:\n|$)", text):
            line = m.group(0)
            end = start + len(line)
            yield line.rstrip("\n"), start, end
            start = end

    def _normalize_heading(self, line: str) -> str | None:
        raw = line.strip()
        if not raw:
            return None

        # Remove numbering like "1. Introduction", "2) Methods", "III RESULTS"
        raw = re.sub(
            r"^\s*(\d+(?:\.\d+)*|[IVXLC]+)\s*[.)]\s*",
            "",
            raw,
            flags=re.IGNORECASE,
        )

        raw = raw.rstrip(" :.\t").strip()

        if len(raw) > 60:
            return None

        lowered = raw.lower()

        for h in self._HEADINGS:
            if lowered == h:
                return h.replace(" & ", " and ")

        return None
