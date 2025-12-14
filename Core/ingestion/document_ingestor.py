# Core/ingestion/document_ingestor.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from Utils.file_loader import load_paper


@dataclass(frozen=True)
class Document:
    """
    Canonical representation of an ingested document.
    This is what ReviewEngine should consume (via doc.text).
    """
    source_path: str
    doc_type: str                 # "pdf" | "txt" | "md" | "unknown"
    text: str
    metadata: Dict[str, Any]


class DocumentIngestor:
    """
    Ingests a file into a Document (text + metadata).
    For now uses Utils.file_loader.load_paper(...) to extract text.
    """

    def ingest(self, path: str | Path) -> Document:
        p = Path(path)
        doc_type = self._infer_type(p)

        text = load_paper(str(p))  # current extractor (we'll improve later)
        text = (text or "").strip()

        metadata: Dict[str, Any] = {
            "filename": p.name,
            "stem": p.stem,
            "suffix": p.suffix.lower(),
            "doc_type": doc_type,
            "size_bytes": p.stat().st_size if p.exists() else None,
        }

        return Document(
            source_path=str(p),
            doc_type=doc_type,
            text=text,
            metadata=metadata,
        )

    @staticmethod
    def _infer_type(p: Path) -> str:
        suf = p.suffix.lower()
        if suf == ".pdf":
            return "pdf"
        if suf in {".txt", ".md"}:
            return suf.lstrip(".")
        return "unknown"
