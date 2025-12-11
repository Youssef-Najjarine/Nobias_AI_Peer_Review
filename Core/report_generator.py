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
        citations = result["citations"]
        plag = result["plagiarism"]
        fraud = result["fraud"]
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

        # Plagiarism / redundancy pieces
        plag_score = plag["overall_plagiarism_suspicion_score"]
        ngram_rep = plag["ngram_repetition_ratio"]
        sent_rep = plag["repeated_sentence_ratio"]

        # Fraud / anomaly pieces
        fraud_score = fraud["overall_fraud_suspicion_score"]
        impossible_p = fraud["impossible_p_values"]
        cluster = fraud["suspicious_p_clustering"]
        extreme_lang = fraud["extreme_effect_language"]
        mismatch = fraud["mismatched_p_text"]

        lines: List[str] = []

        lines.append(f"# Nobias AI Peer Review – {paper_name}\n")

        # High-level snapshot
        lines.append("## Summary Scores\n")
        lines.append(f"- **Bias score**: `{bias_score:.3f}`  (0 = neutral, 1 = highly biased)")
        lines.append(f"- **Statistical rigor score**: `{stats_rigor:.3f}`  (0 = none, 1 = high)")
        lines.append(f"- **Methodology score**: `{meth_score:.3f}`  (0 = weak, 1 = strong)")
        lines.append(
            f"- **Plagiarism / redundancy suspicion score**: `{plag_score:.3f}`  "
            f"(0 = clean, 1 = highly repetitive)"
        )
        lines.append(
            f"- **Fraud / anomaly suspicion score**: `{fraud_score:.3f}`  "
            f"(0 = clean, 1 = highly suspicious)"
        )
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

        # Citations detail
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

        # Plagiarism / redundancy detail
        lines.append("## Plagiarism / Redundancy Signals\n")
        lines.append(
            f"- Overall suspicion score: `{plag_score:.3f}` "
            f"(0 = clean, 1 = highly repetitive)"
        )
        lines.append(
            f"- N-gram repetition ratio (5-grams): `{ngram_rep:.4f}` "
            f"(0 = unique, 1 = extremely repetitive)"
        )
        lines.append(
            f"- Repeated sentence ratio: `{sent_rep:.4f}` "
            f"(0 = no repeated sentences, 1 = mostly repeats)"
        )
        lines.append(
            f"- Top repeated 5-grams: {plag['top_repeated_ngrams']}"
        )
        lines.append(
            f"- Top repeated sentences: {plag['top_repeated_sentences']}"
        )
        lines.append("")

        # Fraud / anomaly detail
        lines.append("## Fraud / Anomaly Signals\n")
        lines.append(
            f"- Overall fraud / anomaly suspicion score: `{fraud_score:.3f}` "
            f"(0 = clean, 1 = highly suspicious)"
        )
        lines.append(
            f"- Impossible or extreme p-values: "
            f"`{impossible_p['count']}` "
            f"(examples: {impossible_p['examples']})"
        )
        lines.append(
            f"- p-values clustered just below 0.05: "
            f"`{cluster['count']}` (cluster ratio: `{cluster['cluster_ratio']:.4f}`) "
            f"(examples: {cluster['examples']})"
        )
        lines.append(
            f"- Extreme effect language occurrences: "
            f"`{extreme_lang['count']}` "
            f"(examples: {extreme_lang['examples']})"
        )
        lines.append(
            f"- Suspected mismatched p-text sentences: "
            f"`{mismatch['count']}` "
            f"(examples: {mismatch['examples']})"
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
