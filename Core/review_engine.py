# Core/review_engine.py
from __future__ import annotations

from typing import Any, Dict

from Core.bias_detector import BiasDetector
from Core.citation_validator import CitationValidator
from Core.ethics_guard import EthicsGuard
from Core.final_verdict_engine import FinalVerdictEngine
from Core.fraud_detector import FraudDetector
from Core.hallucination_guard import HallucinationGuard
from Core.integrity_verifier import IntegrityVerifier
from Core.methodology_validator import MethodologyValidator
from Core.plagiarism_checker import PlagiarismChecker
from Core.reasoning_trace import ReasoningTrace
from Core.replication_simulator import ReplicationSimulator
from Core.statistical_analyzer import StatisticalAnalyzer
from Core.ingestion.document import Document


class ReviewEngine:
    def __init__(self) -> None:
        self.integrity_verifier = IntegrityVerifier()
        self.bias_detector = BiasDetector()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.methodology_validator = MethodologyValidator()
        self.citation_validator = CitationValidator()
        self.plagiarism_checker = PlagiarismChecker()
        self.fraud_detector = FraudDetector()
        self.ethics_guard = EthicsGuard()
        self.replication_simulator = ReplicationSimulator()
        self.hallucination_guard = HallucinationGuard()
        self.trace = ReasoningTrace()
        self.verdict_engine = FinalVerdictEngine()

    def review_paper(self, paper: str | Document) -> Dict[str, Any]:
        # Reset state for new review
        self.trace = ReasoningTrace()
        self.hallucination_guard.audit_history.clear()

        # Normalize input to text
        paper_text: str
        if isinstance(paper, Document):
            paper_text = paper.clean_text
            self.trace.add_step(
                "ingestion",
                "Loaded ingested Document",
                metadata={
                    "doc_type": paper.doc_type,
                    "sections": len(paper.sections),
                    "char_count": paper.char_count,
                }
            )
        else:
            paper_text = str(paper)
            self.trace.add_step("load_paper", "Loaded raw text string")

        # 1. Integrity check
        integrity_result = self.integrity_verifier.check_basic_integrity(paper_text)
        self.trace.add_step("integrity_check", "Completed", integrity_result)

        # 2. Core analyses
        bias_result = self.bias_detector.analyze_text(paper_text)
        stats_result = self.statistical_analyzer.analyze(paper_text)
        methodology_result = self.methodology_validator.analyze(paper_text)

        # === CROSS-WIRING: Methodology rescues Statistics ===
        sample_size_count = methodology_result["sample_size"]["count"]
        if not stats_result["has_statistical_content"] and sample_size_count >= 1:
            stats_result["has_statistical_content"] = True
            if stats_result["overall_rigor_score"] < 0.25:
                stats_result["overall_rigor_score"] = 0.25
            self.trace.add_step(
                "stats_rescue",
                "Statistical content inferred from sample size reporting",
                metadata={
                    "rescued": True,
                    "sample_size_count": sample_size_count,
                    "new_rigor_score": stats_result["overall_rigor_score"]
                }
            )

        # Remaining analyses
        citation_result = self.citation_validator.analyze(paper_text)
        plagiarism_result = self.plagiarism_checker.analyze(paper_text)
        fraud_result = self.fraud_detector.analyze_fraud(paper_text)
        ethics_result = self.ethics_guard.analyze(paper_text)
        replication_result = self.replication_simulator.analyze_replication(
            paper_text,
            stats=stats_result,
            methodology=methodology_result,
            citations=citation_result,
        )

        # === Hallucination Self-Audit on Key Modules ===
        self.hallucination_guard.audit("bias", bias_result, paper_text)
        self.hallucination_guard.audit("statistics", stats_result, paper_text)
        self.hallucination_guard.audit("methodology", methodology_result, paper_text)
        self.hallucination_guard.audit("fraud", fraud_result, paper_text)
        self.hallucination_guard.audit("ethics", ethics_result, paper_text)
        self.hallucination_guard.audit("replication", replication_result, paper_text)

        self.trace.add_step(
            "hallucination_audit",
            "Self-audit completed across modules",
            metadata=self.hallucination_guard.get_overall_audit()
        )

        # Assemble full result
        result: Dict[str, Any] = {
            "integrity": integrity_result,
            "bias": bias_result,
            "statistics": stats_result,
            "methodology": methodology_result,
            "citations": citation_result,
            "plagiarism": plagiarism_result,
            "fraud": fraud_result,
            "ethics": ethics_result,
            "replication": replication_result,
            "hallucination_audit": self.hallucination_guard.get_overall_audit(),
            "hallucination_details": self.hallucination_guard.audit_history,
            "trace": self.trace.export(),
        }

        # Final verdict
        final_verdict = self.verdict_engine.build(result)
        result["final_verdict"] = final_verdict
        self.trace.add_step(
            "final_verdict",
            f"Issued verdict: {final_verdict['verdict_label']}",
            metadata={"trust_score": final_verdict["overall_trust_score"]}
        )

        # Final trace export
        result["trace"] = self.trace.export()

        return result