from pathlib import Path

def load_text_file(path: str) -> str:
    """
    Loads a plain text file and returns its contents as a string.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return p.read_text(encoding="utf-8", errors="ignore")
