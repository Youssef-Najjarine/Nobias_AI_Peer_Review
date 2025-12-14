# Core/reasoning_trace.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class ReasoningTrace:
    """
    Transparent log of every decision step with optional confidence tagging.
    """
    def __init__(self) -> None:
        self._steps: List[Dict[str, Any]] = []

    def add_step(self, tag: str, description: str, metadata: Dict[str, Any] | None = None, confidence: float | None = None) -> None:
        step = {
            "timestamp": datetime.utcnow().isoformat(),
            "tag": tag,
            "description": description,
            "metadata": metadata or {},
        }
        if confidence is not None:
            step["confidence"] = round(confidence, 3)
        self._steps.append(step)

    def export(self) -> List[Dict[str, Any]]:
        return self._steps