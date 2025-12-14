# Core/ingestion/pdf_extractor.py

from __future__ import annotations

from pathlib import Path
import fitz  # PyMuPDF


class PDFExtractor:
    """
    Extracts raw text from PDFs.

    This class does *no* cleaning, normalization, or section parsing.
    That is handled downstream by TextCleaner and Sectionizer.
    """

    def extract_text(self, pdf_path: str | Path) -> str:
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        text_chunks: list[str] = []

        with fitz.open(path) as doc:
            for page in doc:
                page_text = page.get_text("text")
                if page_text:
                    text_chunks.append(page_text)

        return "\n".join(text_chunks)
