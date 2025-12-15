# Security/secure_audit_logs/__init__.py
"""
Secure audit logging configuration
"""
import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

audit_logger = logging.getLogger("nobias_audit")