# Security/secure_audit_logs/logger.py
from __future__ import annotations

from . import audit_logger

def log_event(event: str, details: dict | None = None) -> None:
    msg = event
    if details:
        msg += f" | details: {details}"
    audit_logger.info(msg)