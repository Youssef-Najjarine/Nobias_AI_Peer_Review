# Core/ingestion/ingestor.py
from __future__ import annotations

from pathlib import Path
from Core.ingestion.document import Document
from Core.ingestion.sectionizer import Sectionizer
from Core.ingestion.text_cleaner import TextCleaner
from Utils.pdf_parser import AdvancedPDFExtractor
from Utils.file_loader import load_paper

class DocumentIngestor:
    """
    Advanced ingestor with figure/table detection.
    """
    def __init__(self) -> None:
        self._cleaner = TextCleaner()
        self._sectionizer = Sectionizer()

    def ingest(self, path: Path) -> Document:
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        raw_text = load_paper(str(path))
        cleaned = self._cleaner.clean(raw_text)
        clean_text = cleaned.clean_text
        sections = self._sectionizer.split(clean_text)

        # Advanced extraction if PDF
        figures = []
        tables = []
        page_count = 0
        if path.suffix.lower() == ".pdf":
            extractor = AdvancedPDFExtractor(path)
            data = extractor.extract_all()
            figures = data["figures"]
            tables = data["tables"]
            page_count = data["page_count"]
            extractor.close()

        doc_type = path.suffix.lower().lstrip(".") or "unknown"
        byte_size = path.stat().st_size
        char_count = len(clean_text)

        return Document(
            source_path=path,
            doc_type=doc_type,
            byte_size=byte_size,
            raw_text=raw_text,
            clean_text=clean_text,
            sections=sections,
            char_count=char_count,
            figures=figures,
            tables=tables,
            page_count=page_count,
        )