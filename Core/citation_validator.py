# Core/citation_validator.py

import re
from typing import Dict, Any, List


class CitationValidator:
    """
    Heuristic citation & reference analyzer.

    It looks for:
      - a references/bibliography section
      - DOIs
      - URLs
      - in-text citations (author-year)
      - numeric bracket citations [12], [3,4]
    and produces an overall citation quality score in [0, 1].
    """

    DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/\S+\b", re.IGNORECASE)
    URL_PATTERN = re.compile(r"https?://\S+")
    IN_TEXT_PATTERN = re.compile(
        r"\(([A-Z][A-Za-z]+(?: et al\.)?,?\s*(19|20)\d{2}[a-z]?)\)",
        re.MULTILINE,
    )
    BRACKET_PATTERN = re.compile(r"\[(\d+(?:\s*[,;]\s*\d+)*)\]")

    REF_KEYWORDS = [
        "references",
        "bibliography",
        "works cited",
        "reference list",
    ]

    def _find_references_section(self, text: str) -> List[str]:
        """
        Roughly slice out the references section and return a list of lines
        that look like they belong to the reference list.
        """
        text_lower = text.lower()
        start_idx = None
        for kw in self.REF_KEYWORDS:
            idx = text_lower.find(kw)
            if idx != -1 and (start_idx is None or idx < start_idx):
                start_idx = idx

        if start_idx is None:
            return []

        tail = text[start_idx:]
        lines = tail.splitlines()

        ref_lines: List[str] = []
        for line in lines[1:301]:  # cap to avoid huge tails
            stripped = line.strip()
            if not stripped:
                continue
            # A crude heuristic: year or a period suggests a reference line
            if re.search(r"(19|20)\d{2}", stripped) or "." in stripped:
                ref_lines.append(stripped)

        return ref_lines

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze citation-related structure and return a dictionary with:
            - has_references_section (bool)
            - estimated_reference_count (int)
            - doi, urls, in_text_citations, bracket_citations (counts + examples)
            - overall_citation_quality_score (float)
        """
        if not text.strip():
            return {
                "has_references_section": False,
                "estimated_reference_count": 0,
                "doi": {"count": 0, "examples": []},
                "urls": {"count": 0, "examples": []},
                "in_text_citations": {"count": 0, "examples": []},
                "bracket_citations": {"count": 0, "examples": []},
                "overall_citation_quality_score": 0.0,
            }

        # References section
        ref_lines = self._find_references_section(text)
        has_ref_section = len(ref_lines) > 0
        estimated_ref_count = len(ref_lines)

        # DOIs
        dois = self.DOI_PATTERN.findall(text)
        doi_count = len(dois)

        # URLs
        urls = self.URL_PATTERN.findall(text)
        url_count = len(urls)

        # In-text citations (author-year)
        in_text_examples: List[str] = []
        for m in re.finditer(self.IN_TEXT_PATTERN, text):
            if len(in_text_examples) >= 5:
                break
            in_text_examples.append(m.group(0))
        in_text_count = len(re.findall(self.IN_TEXT_PATTERN, text))

        # Bracket citations [12], [3,4]
        bracket_examples: List[str] = []
        bracket_count = 0
        for m in re.finditer(self.BRACKET_PATTERN, text):
            nums = re.findall(r"\d+", m.group(1))
            bracket_count += len(nums)
            if len(bracket_examples) < 5:
                bracket_examples.append(m.group(0))

        # ------------------------------------------------------------------
        # Scoring
        # ------------------------------------------------------------------
        categories_present = 0
        if has_ref_section:
            categories_present += 1
        if estimated_ref_count > 0:
            categories_present += 1
        if doi_count > 0:
            categories_present += 1
        if url_count > 0:
            categories_present += 1
        if in_text_count > 0 or bracket_count > 0:
            categories_present += 1

        # Diversity component: up to 1.0 from categories
        diversity_score = categories_present / 5.0

        # Volume component: more references → small bump up to +0.25
        volume_score = min(0.25, min(estimated_ref_count, 50) / 200.0)

        overall_score = min(1.0, diversity_score + volume_score)

        return {
            "has_references_section": has_ref_section,
            "estimated_reference_count": estimated_ref_count,
            "doi": {
                "count": doi_count,
                "examples": dois[:5],
            },
            "urls": {
                "count": url_count,
                "examples": urls[:5],
            },
            "in_text_citations": {
                "count": in_text_count,
                "examples": in_text_examples,
            },
            "bracket_citations": {
                "count": bracket_count,
                "examples": bracket_examples,
            },
            "overall_citation_quality_score": overall_score,
        }
