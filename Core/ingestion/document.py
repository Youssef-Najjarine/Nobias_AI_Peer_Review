# Core/ingestion/document.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any

from Core.ingestion.sectionizer import Section


@dataclass(frozen=True)
class Document:
    """
    Canonical ingested document used throughout Nobias_AI.

    This is the ONLY object passed from ingestion → analysis.
    Now includes advanced PDF metadata: figures, tables, page count.
    """

    # Metadata
    source_path: Path
    doc_type: str              # "pdf", "txt", "md", etc.
    byte_size: int             # size on disk

    # Content
    raw_text: str              # raw extraction / load
    clean_text: str            # cleaned version for downstream analysis
    sections: List[Section]    # heuristic splits over clean_text

    # Convenience
    char_count: int            # len(clean_text)

    # Advanced PDF extraction fields (empty for non-PDF)
    figures: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    page_count: int = 0

    def __post_init__(self) -> None:
        if self.char_count != len(self.clean_text):
            raise ValueError("char_count must match len(clean_text)")