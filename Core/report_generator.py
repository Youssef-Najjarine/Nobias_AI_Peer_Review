# noinspection DuplicatedCode

from __future__ import annotations

from pathlib import Path
from typing import Any


class ReportGenerator:
    """
    Generates human-readable review reports (Markdown) from the Nobias
    review result dictionary and saves them to disk.

    Assumes Option A schemas for:
      - fraud
      - replication
    """

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def generate_markdown(paper_name: str, result: dict[str, Any]) -> str:
        integrity = result["integrity"]
        bias = result["bias"]
        stats = result["statistics"]
        meth = result["methodology"]
        citations = result["citations"]
        plag = result["plagiarism"]
        fraud = result["fraud"]                 # Option A
        ethics = result["ethics"]
        replication = result["replication"]     # Option A
        trace: list[dict[str, Any]] = result["trace"]

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
        has_preregistration = meth["transparency"]["has_preregistration"]
        has_data_sharing = meth["transparency"]["has_data_sharing"]

        # Citation pieces
        has_ref_section = citations["has_references_section"]
        est_ref_count = citations["estimated_reference_count"]
        cit_score = citations["overall_citation_quality_score"]

        # Plagiarism / redundancy pieces
        plag_score = plag["overall_plagiarism_suspicion_score"]
        ngram_rep = plag["ngram_repetition_ratio"]
        sent_rep = plag["repeated_sentence_ratio"]

        # Fraud / anomaly pieces (Option A only)
        fraud_score = fraud["overall_fraud_suspicion_score"]
        impossible_p = fraud["impossible_p_values"]
        cluster = fraud["suspicious_p_clustering"]
        extreme_lang = fraud["extreme_effect_language"]
        mismatch = fraud["mismatched_p_text"]

        # Ethics / safety pieces
        ethics_score = ethics["overall_ethics_risk_score"]
        has_human_subjects = ethics["has_human_subjects"]
        has_vulnerable = ethics["has_vulnerable_population"]
        has_ethics_approval = ethics["has_ethics_approval_mention"]
        has_consent = ethics["has_informed_consent_mention"]
        has_data_protection = ethics["mentions_data_protection"]
        risk_terms = ethics["risk_terms"]

        # Replication pieces (Option A only)
        replication_score = replication["overall_replicability_score"]
        simulated_outcome = replication["simulated_replication_outcome"]
        claims = replication["claims"]
        robustness = replication["robustness"]
        openness = replication["openness"]

        lines: list[str] = []

        def _add(*items: str) -> None:
            lines.extend(items)

        def _add_section(title: str, bullet_lines: list[str]) -> None:
            # Helper reduces “duplicated code fragment” inspections by standardizing sections
            _add(title, *bullet_lines, "")

        _add(f"# Nobias AI Peer Review – {paper_name}\n")

        _add_section(
            "## Summary Scores\n",
            [
                f"- **Bias score**: `{bias_score:.3f}`  (0 = neutral, 1 = highly biased)",
                f"- **Statistical rigor score**: `{stats_rigor:.3f}`  (0 = none, 1 = high)",
                f"- **Methodology score**: `{meth_score:.3f}`  (0 = weak, 1 = strong)",
                f"- **Plagiarism / redundancy suspicion score**: `{plag_score:.3f}`  "
                f"(0 = clean, 1 = highly repetitive)",
                f"- **Fraud / anomaly suspicion score**: `{fraud_score:.3f}`  "
                f"(0 = clean, 1 = highly suspicious)",
                f"- **Ethics / safety risk score**: `{ethics_score:.3f}`  "
                f"(0 = low risk, 1 = high risk)",
                f"- **Replicability score**: `{replication_score:.3f}`  "
                f"(0 = fragile, 1 = highly likely to replicate; outcome: `{simulated_outcome}`)",
                f"- **Word count**: `{word_count}`  (passes minimum length: `{passes_min_len}`)",
            ],
        )

        _add_section(
            "## Bias & Language\n",
            [
                f"- Emotional language density: `{emo['density']:.4f}` "
                f"(examples: {emo['examples'][:5]})",
                f"- Authority appeals density: `{auth['density']:.4f}` "
                f"(examples: {auth['examples'][:5]})",
                f"- Certainty language density: `{cert['density']:.4f}` "
                f"(examples: {cert['examples'][:5]})",
            ],
        )

        _add_section(
            "## Statistical Rigor\n",
            [
                f"- Has statistical content: `{has_stats}`",
                f"- P-value count: `{stats['p_values']['count']}` "
                f"(examples: {stats['p_values']['examples']})",
                f"- Confidence interval count: `{stats['confidence_intervals']['count']}` "
                f"(examples: {stats['confidence_intervals']['examples']})",
                f"- Detected tests: {stats['tests']}",
                f"- Effect size / power terms: {stats['effect_terms']}",
            ],
        )

        _add_section(
            "## Methodology & Design\n",
            [
                f"- Sample sizes detected: {sample_sizes}",
                f"- Small-sample warning: `{small_sample_warning}`",
                f"- Has control group: `{has_control}`",
                f"- Has randomization: `{has_randomization}`",
                f"- Has preregistration: `{has_preregistration}`",
                f"- Has data sharing: `{has_data_sharing}`",
            ],
        )

        _add_section(
            "## Replicability & Robustness\n",
            [
                f"- Overall replicability score: `{replication_score:.3f}` "
                f"(simulated outcome: `{simulated_outcome}`)",
                f"- Replication claims: `{claims['has_replication_claims']}`",
                f"- Robustness: bootstrap=`{robustness['mentions_bootstrap']}`, "
                f"monte_carlo=`{robustness['mentions_monte_carlo']}`, "
                f"sensitivity=`{robustness['mentions_sensitivity_analysis']}`",
                f"- Openness: open_data=`{openness['has_open_data']}`, "
                f"open_code=`{openness['has_open_code']}`, "
                f"preregistration=`{openness['has_preregistration']}`",
            ],
        )

        _add_section(
            "## Citations & References\n",
            [
                f"- Has references section: `{has_ref_section}`",
                f"- Estimated reference count: `{est_ref_count}`",
                f"- DOI count: `{citations['doi']['count']}` "
                f"(examples: {citations['doi']['examples']})",
                f"- URL count: `{citations['urls']['count']}` "
                f"(examples: {citations['urls']['examples']})",
                f"- In-text citation count: `{citations['in_text_citations']['count']}` "
                f"(examples: {citations['in_text_citations']['examples']})",
                f"- Bracket citation count: `{citations['bracket_citations']['count']}` "
                f"(examples: {citations['bracket_citations']['examples']})",
                f"- Overall citation quality score: `{cit_score:.3f}`",
            ],
        )

        _add_section(
            "## Plagiarism / Redundancy Signals\n",
            [
                f"- Overall suspicion score: `{plag_score:.3f}` "
                f"(0 = clean, 1 = highly repetitive)",
                f"- N-gram repetition ratio (5-grams): `{ngram_rep:.4f}` "
                f"(0 = unique, 1 = extremely repetitive)",
                f"- Repeated sentence ratio: `{sent_rep:.4f}` "
                f"(0 = no repeated sentences, 1 = mostly repeats)",
                f"- Top repeated 5-grams: {plag['top_repeated_ngrams']}",
                f"- Top repeated sentences: {plag['top_repeated_sentences']}",
            ],
        )

        _add_section(
            "## Fraud / Anomaly Signals\n",
            [
                f"- Overall fraud / anomaly suspicion score: `{fraud_score:.3f}` "
                f"(0 = clean, 1 = highly suspicious)",
                f"- Impossible or extreme p-values: `{impossible_p['count']}` "
                f"(examples: {impossible_p['examples']})",
                f"- p-values clustered just below 0.05: `{cluster['count']}` "
                f"(cluster ratio: `{cluster['cluster_ratio']:.4f}`) "
                f"(examples: {cluster['examples']})",
                f"- Extreme effect language occurrences: `{extreme_lang['count']}` "
                f"(examples: {extreme_lang['examples']})",
                f"- Suspected mismatched p-text sentences: `{mismatch['count']}` "
                f"(examples: {mismatch['examples']})",
            ],
        )

        _add_section(
            "## Ethics & Safety\n",
            [
                f"- Overall ethics / safety risk score: `{ethics_score:.3f}` "
                f"(0 = low risk, 1 = high risk)",
                f"- Has human subjects: `{has_human_subjects}`",
                f"- Has vulnerable population: `{has_vulnerable}`",
                f"- Mentions ethics approval / IRB: `{has_ethics_approval}`",
                f"- Mentions informed consent: `{has_consent}`",
                f"- Mentions data protection / privacy: `{has_data_protection}`",
                f"- High-risk / dual-use terms: `{risk_terms['count']}` "
                f"(examples: {risk_terms['examples']})",
            ],
        )

        _add_section(
            "## Integrity Checks\n",
            [
                f"- Is empty: `{integrity['is_empty']}`",
                f"- Word count: `{word_count}`",
                f"- Passes minimum word length threshold: `{passes_min_len}`",
            ],
        )

        _add("## Reasoning Trace (first steps)\n")
        for step in trace[:10]:
            ts = step["timestamp"]
            tag = step["tag"]
            desc = step["description"]
            _add(f"- **[{tag}]** `{ts}` – {desc}")
            if step.get("metadata"):
                _add(f"  - metadata: `{step['metadata']}`")
        _add("")

        return "\n".join(lines)

    def save_markdown(self, paper_name: str, result: dict[str, Any]) -> Path:
        md = self.generate_markdown(paper_name, result)
        safe_name = paper_name.replace(" ", "_")
        out_path = self.output_dir / f"{safe_name}_review.md"
        out_path.write_text(md, encoding="utf-8")
        return out_path
