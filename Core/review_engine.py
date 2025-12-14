# Core/review_engine.py

from __future__ import annotations

from typing import Any, Dict

from Core.integrity_verifier import IntegrityVerifier
from Core.bias_detector import BiasDetector
from Core.statistical_analyzer import StatisticalAnalyzer
from Core.methodology_validator import MethodologyValidator
from Core.citation_validator import CitationValidator
from Core.plagiarism_checker import PlagiarismChecker
from Core.fraud_detector import FraudDetector
from Core.ethics_guard import EthicsGuard
from Core.replication_simulator import ReplicationSimulator
from Core.reasoning_trace import ReasoningTrace
from Core.final_verdict_engine import FinalVerdictEngine
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
        self.trace = ReasoningTrace()
        self.verdict_engine = FinalVerdictEngine()

    def review_paper(self, paper: str | Document) -> Dict[str, Any]:
        # Reset trace each run
        self.trace = ReasoningTrace()

        # Normalize input to text (and optionally capture ingestion metadata)
        paper_text: str
        if isinstance(paper, Document):
            paper_text = paper.clean_text
            self.trace.add_step(
                "ingestion",
                "Using ingested Document (clean_text).",
                metadata={
                    "doc_type": paper.doc_type,
                    "byte_size": paper.byte_size,
                    "raw_char_count": len(paper.raw_text),
                    "clean_char_count": paper.char_count,
                    "section_count": len(paper.sections),
                },
            )
        else:
            paper_text = paper
            self.trace.add_step("load_paper", "Loaded paper text into review engine.")

        # 1) Integrity
        integrity_result = self.integrity_verifier.check_basic_integrity(paper_text)
        self.trace.add_step(
            "integrity_check",
            f"Word count={integrity_result['word_count']}, "
            f"passes_minimum_length={integrity_result['passes_minimum_length']}",
        )

        # 2) Bias
        bias_result = self.bias_detector.analyze_text(paper_text)
        self.trace.add_step(
            "bias_analysis",
            f"Overall bias score={bias_result['overall_bias_score']:.4f}",
            metadata={
                "emotional_density": bias_result["emotional_language"]["density"],
                "authority_density": bias_result["authority_appeals"]["density"],
                "certainty_density": bias_result["certainty_language"]["density"],
            },
        )

        # 3) Stats
        stats_result = self.statistical_analyzer.analyze(paper_text)

        # 4) Methodology
        methodology_result = self.methodology_validator.analyze(paper_text)

        # 5) Cross-wiring: methodology can “rescue” stats
        sample_size_count = methodology_result["sample_size"]["count"]
        if not stats_result["has_statistical_content"] and sample_size_count >= 1:
            stats_result["has_statistical_content"] = True
            if stats_result["overall_rigor_score"] < 0.25:
                stats_result["overall_rigor_score"] = 0.25

        # 6) Citations
        citation_result = self.citation_validator.analyze(paper_text)

        # 7) Plagiarism
        plagiarism_result = self.plagiarism_checker.analyze(paper_text)

        # 8) Fraud (Option A)
        fraud_result = self.fraud_detector.analyze_fraud(paper_text)

        # 9) Ethics
        ethics_result = self.ethics_guard.analyze(paper_text)

        # 10) Replication (Option A)
        replication_result = self.replication_simulator.analyze_replication(
            paper_text,
            stats=stats_result,
            methodology=methodology_result,
            citations=citation_result,
        )

        # ---- Trace entries ----
        self.trace.add_step(
            "statistical_analysis",
            f"Overall rigor score={stats_result['overall_rigor_score']:.4f}",
            metadata={
                "has_statistical_content": stats_result["has_statistical_content"],
                "p_value_count": stats_result["p_values"]["count"],
                "ci_count": stats_result["confidence_intervals"]["count"],
            },
        )

        self.trace.add_step(
            "methodology_analysis",
            f"Overall methodology score={methodology_result['overall_methodology_score']:.4f}",
            metadata={
                "sample_size_count": sample_size_count,
                "small_sample_warning": methodology_result["sample_size"]["small_sample_warning"],
                "has_control_group": methodology_result["control_and_blinding"]["has_control_group"],
                "has_randomization": methodology_result["design"]["has_randomization"],
            },
        )

        self.trace.add_step(
            "fraud_analysis",
            f"Overall fraud suspicion score={fraud_result['overall_fraud_suspicion_score']:.4f}",
            metadata={
                "impossible_p_count": fraud_result["impossible_p_values"]["count"],
                "cluster_ratio": fraud_result["suspicious_p_clustering"]["cluster_ratio"],
                "mismatch_count": fraud_result["mismatched_p_text"]["count"],
                "signals": fraud_result.get("signals", {}),
            },
        )

        self.trace.add_step(
            "ethics_analysis",
            f"Overall ethics / safety risk score={ethics_result['overall_ethics_risk_score']:.4f}",
            metadata={
                "has_human_subjects": ethics_result["has_human_subjects"],
                "has_vulnerable_population": ethics_result["has_vulnerable_population"],
                "has_ethics_approval_mention": ethics_result["has_ethics_approval_mention"],
            },
        )

        self.trace.add_step(
            "replication_analysis",
            f"Overall replicability score={replication_result['overall_replicability_score']:.4f}",
            metadata={
                "outcome": replication_result["simulated_replication_outcome"],
                "claims": replication_result["claims"],
                "robustness": replication_result["robustness"],
                "openness": replication_result["openness"],
            },
        )

        # ---- Assemble result (Option A) ----
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
            "trace": self.trace.export(),
        }

        # ---- Final Verdict (product-style) ----
        final_verdict = self.verdict_engine.build(result)
        result["final_verdict"] = final_verdict

        self.trace.add_step(
            "final_verdict",
            f"Verdict={final_verdict['verdict_label']}, trust={final_verdict['overall_trust_score']:.2f}",
            metadata={"reasons": final_verdict["reasons"]},
        )
        result["trace"] = self.trace.export()

        return result
