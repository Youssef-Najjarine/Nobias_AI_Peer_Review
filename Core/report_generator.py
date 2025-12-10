# Core/report_generator.py

from pathlib import Path
from typing import Dict, Any, List


class ReportGenerator:
    """
    Generates human-readable review reports (Markdown) from the Nobias
    review result dictionary and saves them to disk.
    """

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown(self, paper_name: str, result: Dict[str, Any]) -> str:
        integrity = result["integrity"]
        bias = result["bias"]
        stats = result["statistics"]
        meth = result["methodology"]
        citations = result["citations"]          # <-- NEW
        trace: List[Dict[str, Any]] = result["trace"]

        # Pull some handy pieces
        word_count = integrity["word_count"]
        passes_min_len = integrity["passes_minimum_length"]

        bias_score = bias["overall_bias_score"]
        emo = bias["emotional_language"]
        auth = bias["authority_appeals"]
        cert = bias["certainty_language"]

        stats_rigor = stats["overall_rigor_score"]
        has_stats = stats["has_statistical_content"]

        meth_score = meth["overall_methodology_score"]
        sample_sizes = meth["sample_size"]["values"]
        small_sample_warning = meth["sample_size"]["small_sample_warning"]
        has_control = meth["control_and_blinding"]["has_control_group"]
        has_randomization = meth["design"]["has_randomization"]
        has_prereg = meth["transparency"]["has_preregistration"]
        has_data_sharing = meth["transparency"]["has_data_sharing"]

        # Citation pieces
        has_ref_section = citations["has_references_section"]
        est_ref_count = citations["estimated_reference_count"]
        cit_score = citations["overall_citation_quality_score"]

        lines: List[str] = []

        lines.append(f"# Nobias AI Peer Review – {paper_name}\n")

        # High-level snapshot
        lines.append("## Summary Scores\n")
        lines.append(f"- **Bias score**: `{bias_score:.3f}`  (0 = neutral, 1 = highly biased)")
        lines.append(f"- **Statistical rigor score**: `{stats_rigor:.3f}`  (0 = none, 1 = high)")
        lines.append(f"- **Methodology score**: `{meth_score:.3f}`  (0 = weak, 1 = strong)")
        lines.append(f"- **Word count**: `{word_count}`  "
                     f"(passes minimum length: `{passes_min_len}`)")
        lines.append("")

        # Bias detail
        lines.append("## Bias & Language\n")
        lines.append(f"- Emotional language density: `{emo['density']:.4f}` "
                     f"(examples: {emo['examples'][:5]})")
        lines.append(f"- Authority appeals density: `{auth['density']:.4f}` "
                     f"(examples: {auth['examples'][:5]})")
        lines.append(f"- Certainty language density: `{cert['density']:.4f}` "
                     f"(examples: {cert['examples'][:5]})")
        lines.append("")

        # Stats detail
        lines.append("## Statistical Rigor\n")
        lines.append(f"- Has statistical content: `{has_stats}`")
        lines.append(f"- P-value count: `{stats['p_values']['count']}` "
                     f"(examples: {stats['p_values']['examples']})")
        lines.append(f"- Confidence interval count: "
                     f"`{stats['confidence_intervals']['count']}` "
                     f"(examples: {stats['confidence_intervals']['examples']})")
        lines.append(f"- Detected tests: {stats['tests']}")
        lines.append(f"- Effect size / power terms: {stats['effect_terms']}")
        lines.append("")

        # Methodology detail
        lines.append("## Methodology & Design\n")
        lines.append(f"- Sample sizes detected: {sample_sizes}")
        lines.append(f"- Small-sample warning: `{small_sample_warning}`")
        lines.append(f"- Has control group: `{has_control}`")
        lines.append(f"- Has randomization: `{has_randomization}`")
        lines.append(f"- Has preregistration: `{has_prereg}`")
        lines.append(f"- Has data sharing: `{has_data_sharing}`")
        lines.append("")

        # 🔹 NEW: Citations detail
        lines.append("## Citations & References\n")
        lines.append(f"- Has references section: `{has_ref_section}`")
        lines.append(f"- Estimated reference count: `{est_ref_count}`")
        lines.append(
            f"- DOI count: `{citations['doi']['count']}` "
            f"(examples: {citations['doi']['examples']})"
        )
        lines.append(
            f"- URL count: `{citations['urls']['count']}` "
            f"(examples: {citations['urls']['examples']})"
        )
        lines.append(
            f"- In-text citation count: `{citations['in_text_citations']['count']}` "
            f"(examples: {citations['in_text_citations']['examples']})"
        )
        lines.append(
            f"- Bracket citation count: `{citations['bracket_citations']['count']}` "
            f"(examples: {citations['bracket_citations']['examples']})"
        )
        lines.append(
            f"- Overall citation quality score: `{cit_score:.3f}`"
        )
        lines.append("")

        # Integrity detail
        lines.append("## Integrity Checks\n")
        lines.append(f"- Is empty: `{integrity['is_empty']}`")
        lines.append(f"- Word count: `{word_count}`")
        lines.append(f"- Passes minimum word length threshold: `{passes_min_len}`")
        lines.append("")

        # Reasoning trace – first few steps
        lines.append("## Reasoning Trace (first steps)\n")
        for step in trace[:10]:
            ts = step["timestamp"]
            tag = step["tag"]
            desc = step["description"]
            lines.append(f"- **[{tag}]** `{ts}` – {desc}")
            if step.get("metadata"):
                lines.append(f"  - metadata: `{step['metadata']}`")
        lines.append("")

        return "\n".join(lines)

    def save_markdown(self, paper_name: str, result: Dict[str, Any]) -> Path:
        """
        Builds a safe filename from the paper name, writes the markdown report,
        and returns the Path to the file.
        """
        md = self.generate_markdown(paper_name, result)
        safe_name = paper_name.replace(" ", "_")
        out_path = self.output_dir / f"{safe_name}_review.md"
        out_path.write_text(md, encoding="utf-8")
        return out_path
