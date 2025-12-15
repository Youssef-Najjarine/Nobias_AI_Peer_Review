# Security/tamper_detection.py
from __future__ import annotations

import hashlib
from pathlib import Path

class TamperDetector:
    """
    Detects tampering in generated reports by verifying hashes.
    """
    def __init__(self, hash_store_path: Path):
        self.hash_store = hash_store_path
        self.hash_store.parent.mkdir(parents=True, exist_ok=True)
        if not self.hash_store.exists():
            self.hash_store.write_text("{}")

    def store_hash(self, file_path: Path, file_hash: str, metadata: str = "") -> None:
        data = {}
        if self.hash_store.read_text():
            import json
            data = json.loads(self.hash_store.read_text())
        data[str(file_path)] = {"hash": file_hash, "metadata": metadata}
        self.hash_store.write_text(json.dumps(data, indent=2))

    def verify(self, file_path: Path) -> bool:
        if not file_path.exists():
            return False
        current_hash = self._hash_file(file_path)
        import json
        stored = json.loads(self.hash_store.read_text() or "{}")
        stored_entry = stored.get(str(file_path), {})
        return stored_entry.get("hash") == current_hash

    @staticmethod
    def _hash_file(path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()