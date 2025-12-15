# Utils/file_loader.py
from pathlib import Path
from Utils.pdf_parser import AdvancedPDFExtractor

def load_paper(path: str | Path) -> str:
    """
    High-level loader for scientific papers.
    Uses AdvancedPDFExtractor for PDFs.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Paper not found: {path}")

    suffix = p.suffix.lower()
    if suffix == ".pdf":
        extractor = AdvancedPDFExtractor(p)
        data = extractor.extract_all()
        extractor.close()
        return data["text"]  # For now return text; full data can be used later
    else:
        # Fallback for text files
        return p.read_text(encoding="utf-8", errors="ignore")