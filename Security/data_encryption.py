# Security/data_encryption.py
from __future__ import annotations

from cryptography.fernet import Fernet
from typing import Optional

class DataEncryptor:
    """
    Simple AES encryption for sensitive data (e.g., review_history).
    Key should be loaded from environment in production.
    """
    def __init__(self, key: Optional[bytes] = None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode("utf-8"))

    def decrypt(self, token: bytes) -> str:
        return self.cipher.decrypt(token).decode("utf-8")

    def get_key(self) -> bytes:
        return self.key