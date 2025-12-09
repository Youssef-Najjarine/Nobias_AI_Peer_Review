class IntegrityVerifier:
    """
    Very early stub for checking basic paper integrity.
    Later this will handle consistency checks, anomaly detection, etc.
    """

    def check_basic_integrity(self, paper_text: str) -> dict:
        """
        For now, just returns a toy result indicating whether the
        paper has a minimum length and is non-empty.
        """
        stripped = paper_text.strip()
        word_count = len(stripped.split()) if stripped else 0

        return {
            "is_empty": word_count == 0,
            "word_count": word_count,
            "passes_minimum_length": word_count >= 100,  # arbitrary for now
        }
