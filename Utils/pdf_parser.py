# Utils/pdf_parser.py

from pathlib import Path
from typing import Optional

from PyPDF2 import PdfReader


def extract_text_from_pdf(path: str, max_pages: Optional[int] = None) -> str:
    """
    Extracts text from a PDF file using PyPDF2.

    :param path: Path to the PDF file.
    :param max_pages: Optional limit on how many pages to read
                      (useful for huge documents while testing).
    :return: Extracted text as a single string.
    """
    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    reader = PdfReader(str(pdf_path))

    texts: list[str] = []
    num_pages = len(reader.pages)

    if max_pages is not None:
        num_pages = min(num_pages, max_pages)

    for i in range(num_pages):
        page = reader.pages[i]
        page_text = page.extract_text() or ""
        texts.append(page_text)

    return "\n\n".join(texts)
