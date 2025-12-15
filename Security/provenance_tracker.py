# Security/provenance_tracker.py
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Any

class ProvenanceTracker:
    """
    Tracks provenance of inputs and outputs for auditability.
    """
    @staticmethod
    def hash_file(path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def track_input(file_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "input_hash": ProvenanceTracker.hash_file(file_path),
            "file_size": file_path.stat().st_size,
            "metadata": metadata,
        }

    @staticmethod
    def track_output(report_path: Path, input_provenance: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "output_hash": ProvenanceTracker.hash_file(report_path),
            "input_provenance": input_provenance,
        }