# Core/__init__.py
from .bias_detector import BiasDetector
from .citation_validator import CitationValidator
from .ethics_guard import EthicsGuard
from .final_verdict_engine import FinalVerdictEngine
from .fraud_detector import FraudDetector
from .hallucination_guard import HallucinationGuard  # ← NEW
from .integrity_verifier import IntegrityVerifier
from .methodology_validator import MethodologyValidator
from .plagiarism_checker import PlagiarismChecker
from .reasoning_trace import ReasoningTrace
from .replication_simulator import ReplicationSimulator
from .report_generator import ReportGenerator
from .review_engine import ReviewEngine
from .statistical_analyzer import StatisticalAnalyzer

# Ingestion submodule
from .ingestion import (
    Document,
    DocumentIngestor,
    Section,
    Sectionizer,
    CleanedText,
    TextCleaner,
)

__all__ = [
    "BiasDetector",
    "CitationValidator",
    "EthicsGuard",
    "FinalVerdictEngine",
    "FraudDetector",
    "HallucinationGuard",  # ← NEW
    "IntegrityVerifier",
    "MethodologyValidator",
    "PlagiarismChecker",
    "ReasoningTrace",
    "ReplicationSimulator",
    "ReportGenerator",
    "ReviewEngine",
    "StatisticalAnalyzer",
    "Document",
    "DocumentIngestor",
    "Section",
    "Sectionizer",
    "CleanedText",
    "TextCleaner",
]