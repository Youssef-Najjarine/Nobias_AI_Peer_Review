# Tests/test_security_layer.py
from Security.sandbox_executor import SandboxExecutor
from Security.data_encryption import DataEncryptor
from Security.provenance_tracker import ProvenanceTracker
from Security.tamper_detection import TamperDetector
from pathlib import Path
import tempfile
import os


def test_sandbox_execution():
    executor = SandboxExecutor(timeout_seconds=5)
    result = executor.execute_code("print('Hello')")
    assert result["success"] is True
    assert "Hello" in result["output"]


def test_encryption_roundtrip():
    encryptor = DataEncryptor()
    original = "sensitive data"
    encrypted = encryptor.encrypt(original)
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == original


def test_provenance_tracking():
    # Fixed: Use delete=False on Windows to avoid PermissionError
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(b"test content")
        tmp.close()  # Explicitly close to release handle on Windows

    try:
        provenance = ProvenanceTracker.track_input(tmp_path, {"test": True})
        assert "input_hash" in provenance
        assert len(provenance["input_hash"]) == 64  # SHA256 hex
        assert provenance["file_size"] > 0
    finally:
        # Clean up the temp file
        if tmp_path.exists():
            tmp_path.unlink()


def test_tamper_detection(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("original")
    detector = TamperDetector(tmp_path / "hashes.json")
    original_hash = detector._hash_file(file)
    detector.store_hash(file, original_hash)

    assert detector.verify(file) is True

    file.write_text("tampered")
    assert detector.verify(file) is False