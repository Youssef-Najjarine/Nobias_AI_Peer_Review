# Security/sandbox_executor.py
from __future__ import annotations

import subprocess
import tempfile
import os
from typing import Dict, Any
from pathlib import Path

class SandboxExecutor:
    """
    Secure sandbox for executing untrusted code snippets (e.g., from papers claiming reproducibility).
    Uses restricted environment and timeout.
    """
    def __init__(self, timeout_seconds: int = 30):
        self.timeout = timeout_seconds

    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        if language != "python":
            return {"error": "Only Python execution supported", "output": "", "success": False}

        with tempfile.TemporaryDirectory() as tmpdir:
            code_path = Path(tmpdir) / "script.py"
            code_path.write_text(code, encoding="utf-8")

            try:
                result = subprocess.run(
                    ["python", str(code_path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir,
                    env={"PATH": ""}  # Restricted environment
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "return_code": result.returncode,
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": f"Execution timed out after {self.timeout} seconds",
                    "output": "",
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "output": "",
                }