from datetime import datetime

class ReasoningTrace:
    """
    Keeps a transparent record of every step the system takes
    while reviewing a paper.
    """

    def __init__(self):
        self._steps = []

    def add_step(self, tag: str, description: str, metadata: dict | None = None):
        self._steps.append({
            "timestamp": datetime.utcnow().isoformat(),
            "tag": tag,
            "description": description,
            "metadata": metadata or {},
        })

    def export(self) -> list[dict]:
        """
        Returns the reasoning trace as a list of dicts that can be
        serialized to JSON.
        """
        return self._steps
