# Tests/test_citation_validation.py
from Core.citation_validator import CitationValidator

def test_citation_validator_detects_references():
    validator = CitationValidator()
    text = """
    References
    Smith et al. (2020). DOI: 10.1234/example
    Jones (2019). https://example.com
    """
    result = validator.analyze(text)

    assert result["has_references_section"] is True
    assert result["doi"]["count"] >= 1
    assert result["overall_citation_quality_score"] > 0.5