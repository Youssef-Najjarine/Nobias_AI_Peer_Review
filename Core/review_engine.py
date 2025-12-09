# Core/review_engine.py

from Core.reasoning_trace import ReasoningTrace
from Core.integrity_verifier import IntegrityVerifier
from Core.bias_detector import BiasDetector
from Core.statistical_analyzer import StatisticalAnalyzer
from Core.methodology_validator import MethodologyValidator


class ReviewEngine:
    """
    Central orchestrator for the Nobias AI Peer Review process.
    """

    def __init__(self):
        self.trace = ReasoningTrace()
        self.integrity_verifier = IntegrityVerifier()
        self.bias_detector = BiasDetector()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.methodology_validator = MethodologyValidator()

    def review_paper(self, paper_text: str) -> dict:
        """
        Main entry point for running a review on a paper's text.
        Currently performs:
          1) basic integrity checks
          2) rule-based bias analysis
          3) statistical rigor analysis
          4) methodology / design analysis
        and returns a structured result + reasoning trace.
        """
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

        # 3) Statistical rigor analysis
        stats_result = self.statistical_analyzer.analyze(paper_text)
        self.trace.add_step(
            "statistical_analysis",
            f"Overall rigor score={stats_result['overall_rigor_score']:.4f}",
            metadata={
                "has_statistical_content": stats_result["has_statistical_content"],
                "p_value_count": stats_result["p_values"]["count"],
                "ci_count": stats_result["confidence_intervals"]["count"],
            },
        )

        # 4) Methodology / design analysis
        methodology_result = self.methodology_validator.analyze(paper_text)
        self.trace.add_step(
            "methodology_analysis",
            f"Overall methodology score="
            f"{methodology_result['overall_methodology_score']:.4f}",
            metadata={
                "sample_size_count": methodology_result["sample_size"]["count"],
                "small_sample_warning": methodology_result["sample_size"]["small_sample_warning"],
                "has_control_group": methodology_result["control_and_blinding"]["has_control_group"],
                "has_randomization": methodology_result["design"]["has_randomization"],
            },
        )

        return {
            "integrity": integrity_result,
            "bias": bias_result,
            "statistics": stats_result,
            "methodology": methodology_result,
            "trace": self.trace.export(),
        }
