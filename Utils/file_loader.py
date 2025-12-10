# Utils/file_loader.py

from pathlib import Path

from Utils.pdf_parser import extract_text_from_pdf


def load_text_file(path: str) -> str:
    """
    Loads a plain text file and returns its contents as a string.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return p.read_text(encoding="utf-8", errors="ignore")


def load_paper(path: str) -> str:
    """
    High-level loader for a scientific paper.

    - If it's a .pdf -> uses PDF parser.
    - Otherwise -> tries to load as plain text.

    This is the function you should use from the ReviewEngine / main.py.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Paper not found: {path}")

    suffix = p.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(str(p))
    else:
        # You can later expand to handle .md, .tex, etc.
        return load_text_file(str(p))
