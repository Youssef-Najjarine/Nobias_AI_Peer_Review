# Core/review_engine.py

from Core.integrity_verifier import IntegrityVerifier
from Core.bias_detector import BiasDetector
from Core.statistical_analyzer import StatisticalAnalyzer
from Core.methodology_validator import MethodologyValidator
from Core.citation_validator import CitationValidator
from Core.reasoning_trace import ReasoningTrace


class ReviewEngine:
    def __init__(self):
        # Core analysis components
        self.integrity_verifier = IntegrityVerifier()
        self.bias_detector = BiasDetector()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.methodology_validator = MethodologyValidator()
        self.citation_validator = CitationValidator()   # <-- NEW

        # Reasoning trace logger (this is what was missing)
        self.trace = ReasoningTrace()

    def review_paper(self, paper_text: str) -> dict:
        """
        Main entry point for running a review on a paper's text.
        Performs:
          1) basic integrity checks
          2) rule-based bias analysis
          3) statistical rigor analysis
          4) methodology / design analysis
          5) cross-wiring: methodology can upgrade stats flags
          6) citation / reference analysis
        and returns a structured result + reasoning trace.
        """
        # --- 0) initial trace entry ---
        self.trace.add_step("load_paper", "Loaded paper text into review engine.")

        # 1) Integrity check
        integrity_result = self.integrity_verifier.check_basic_integrity(paper_text)
        self.trace.add_step(
            "integrity_check",
            f"Word count={integrity_result['word_count']}, "
            f"passes_minimum_length={integrity_result['passes_minimum_length']}",
        )

        # 2) Bias analysis
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

        # 3) Statistical rigor analysis (initial)
        stats_result = self.statistical_analyzer.analyze(paper_text)

        # 4) Methodology / design analysis
        methodology_result = self.methodology_validator.analyze(paper_text)

        # 5) Cross-wiring: upgrade stats if methodology clearly shows study-like structure
        sample_size_count = methodology_result["sample_size"]["count"]
        if not stats_result["has_statistical_content"] and sample_size_count >= 1:
            stats_result["has_statistical_content"] = True
            if stats_result["overall_rigor_score"] < 0.25:
                stats_result["overall_rigor_score"] = 0.25

        # 6) Citation / reference analysis
        citation_result = self.citation_validator.analyze(paper_text)

        # --- Trace entries using final values ---
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
            f"Overall methodology score="
            f"{methodology_result['overall_methodology_score']:.4f}",
            metadata={
                "sample_size_count": sample_size_count,
                "small_sample_warning": methodology_result["sample_size"]["small_sample_warning"],
                "has_control_group": methodology_result["control_and_blinding"]["has_control_group"],
                "has_randomization": methodology_result["design"]["has_randomization"],
            },
        )

        self.trace.add_step(
            "citation_analysis",
            f"Overall citation quality score="
            f"{citation_result['overall_citation_quality_score']:.4f}",
            metadata={
                "has_references_section": citation_result["has_references_section"],
                "estimated_reference_count": citation_result["estimated_reference_count"],
                "doi_count": citation_result["doi"]["count"],
            },
        )

        return {
            "integrity": integrity_result,
            "bias": bias_result,
            "statistics": stats_result,
            "methodology": methodology_result,
            "citations": citation_result,
            "trace": self.trace.export(),
        }
