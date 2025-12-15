# Utils/pdf_parser.py
from __future__ import annotations

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re

class AdvancedPDFExtractor:
    """
    Advanced PDF extraction using PyMuPDF (fitz).
    Extracts text, detects figures and tables, preserves reading order.
    """
    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")
        self.doc = fitz.open(self.path)

    def extract_text(self) -> str:
        """Extract clean text preserving reading order."""
        text_blocks = []
        for page in self.doc:
            blocks = page.get_text("blocks", sort=True)  # sort=True preserves reading order
            for block in blocks:
                text = block[4].strip()  # block text
                if text:
                    text_blocks.append(text)
        return "\n\n".join(text_blocks)

    def detect_figures(self) -> List[Dict[str, Any]]:
        """Detect figures by image blocks."""
        figures = []
        for page_num, page in enumerate(self.doc, start=1):
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                figures.append({
                    "page": page_num,
                    "image_index": img_index,
                    "width": img[2],
                    "height": img[3],
                    "ext": base_image["ext"],
                    "size_bytes": len(base_image["image"]),
                })
        return figures

    def detect_tables(self) -> List[Dict[str, Any]]:
        """Simple table detection via horizontal/vertical lines and text density."""
        tables = []
        for page_num, page in enumerate(self.doc, start=1):
            # Get drawings (lines)
            drawings = page.get_drawings()
            horiz_lines = [d for d in drawings if abs(d["rect"][3] - d["rect"][1]) < 5]  # thin horizontal
            vert_lines = [d for d in drawings if abs(d["rect"][2] - d["rect"][0]) < 5]  # thin vertical

            if len(horiz_lines) > 4 and len(vert_lines) > 2:  # heuristic for table
                # Get text in page
                text_blocks = page.get_text("dict")["blocks"]
                table_text = [b["lines"] for b in text_blocks if b["type"] == 0]
                tables.append({
                    "page": page_num,
                    "line_count": len(table_text),
                    "horiz_lines": len(horiz_lines),
                    "vert_lines": len(vert_lines),
                    "confidence": "high" if len(horiz_lines) > 8 else "medium",
                })
        return tables

    def extract_all(self) -> Dict[str, Any]:
        """Extract everything in one call."""
        return {
            "text": self.extract_text(),
            "figures": self.detect_figures(),
            "tables": self.detect_tables(),
            "page_count": len(self.doc),
            "metadata": self.doc.metadata,
        }

    def close(self):
        self.doc.close()