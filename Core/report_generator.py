# Core/report_generator.py

from __future__ import annotations

from pathlib import Path
from typing import Any


class ReportGenerator:
    """
    Generates human-readable review reports (Markdown) from the Nobias
    review result dictionary and saves them to disk.

    Assumes Option A schemas for all sections, including:
      - fraud
      - replication
      - final_verdict
    """

    def __init__(self, output_dir: str | Path = "reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown(self, paper_name: str, result: dict[str, Any]) -> str:
        integrity: dict[str, Any] = result["integrity"]
        bias: dict[str, Any] = result["bias"]
        stats: dict[str, Any] = result["statistics"]
        meth: dict[str, Any] = result["methodology"]
        citations: dict[str, Any] = result["citations"]
        plag: dict[str, Any] = result["plagiarism"]
        fraud: dict[str, Any] = result["fraud"]
        ethics: dict[str, Any] = result["ethics"]
        replication: dict[str, Any] = result["replication"]
        final_verdict: dict[str, Any] = result["final_verdict"]
        trace: list[dict[str, Any]] = result["trace"]

        # --- Handy pieces ---
        word_count = int(integrity["word_count"])
        passes_min_len = bool(integrity["passes_minimum_length"])

        bias_score = float(bias["overall_bias_score"])
        emo: dict[str, Any] = bias["emotional_language"]
        auth: dict[str, Any] = bias["authority_appeals"]
        cert: dict[str, Any] = bias["certainty_language"]

        stats_rigor = float(stats["overall_rigor_score"])
        has_stats = bool(stats["has_statistical_content"])

        meth_score = float(meth["overall_methodology_score"])
        sample_sizes = meth["sample_size"]["values"]
        small_sample_warning = bool(meth["sample_size"]["small_sample_warning"])
        has_control = bool(meth["control_and_blinding"]["has_control_group"])
        has_randomization = bool(meth["design"]["has_randomization"])
        has_preregistration = bool(meth["transparency"]["has_preregistration"])
        has_data_sharing = bool(meth["transparency"]["has_data_sharing"])

        has_ref_section = bool(citations["has_references_section"])
        est_ref_count = int(citations["estimated_reference_count"])
        cit_score = float(citations["overall_citation_quality_score"])

        plag_score = float(plag["overall_plagiarism_suspicion_score"])
        ngram_rep = float(plag["ngram_repetition_ratio"])
        sent_rep = float(plag["repeated_sentence_ratio"])

        fraud_score = float(fraud["overall_fraud_suspicion_score"])
        impossible_p: dict[str, Any] = fraud["impossible_p_values"]
        cluster: dict[str, Any] = fraud["suspicious_p_clustering"]
        extreme_lang: dict[str, Any] = fraud["extreme_effect_language"]
        mismatch: dict[str, Any] = fraud["mismatched_p_text"]

        ethics_score = float(ethics["overall_ethics_risk_score"])
        has_human_subjects = bool(ethics["has_human_subjects"])
        has_vulnerable = bool(ethics["has_vulnerable_population"])
        has_ethics_approval = bool(ethics["has_ethics_approval_mention"])
        has_consent = bool(ethics["has_informed_consent_mention"])
        has_data_protection = bool(ethics["mentions_data_protection"])
        risk_terms: dict[str, Any] = ethics["risk_terms"]

        replication_score = float(replication["overall_replicability_score"])
        simulated_outcome = str(replication["simulated_replication_outcome"])
        claims: dict[str, Any] = replication["claims"]
        robustness: dict[str, Any] = replication["robustness"]
        openness: dict[str, Any] = replication["openness"]

        trust_score = float(final_verdict["overall_trust_score"])
        verdict_label = str(final_verdict["verdict_label"])
        reasons_raw = final_verdict["reasons"]
        reasons: list[str] = [str(r) for r in reasons_raw]

        lines: list[str] = []

        def _add(*items: str) -> None:
            lines.extend(items)

        _add(f"# Nobias AI Peer Review – {paper_name}\n")

        # ✅ Product-style Final Verdict at the top
        _add(
            "## Final Verdict\n",
            f"- **Verdict**: **{verdict_label}**",
            f"- **Overall trust score**: `{trust_score:.2f}` (0.00–1.00; higher is better)",
            "",
            "### Key Reasons",
        )
        for r in reasons[:5]:
            _add(f"- {r}")
        _add("")

        # High-level snapshot
        _add(
            "## Summary Scores\n",
            f"- **Bias score**: `{bias_score:.3f}`  (0 = neutral, 1 = highly biased)",
            f"- **Statistical rigor score**: `{stats_rigor:.3f}`  (0 = none, 1 = high)",
            f"- **Methodology score**: `{meth_score:.3f}`  (0 = weak, 1 = strong)",
            f"- **Citation quality score**: `{cit_score:.3f}`  (0 = weak, 1 = strong)",
            f"- **Plagiarism / redundancy suspicion score**: `{plag_score:.3f}`  (0 = clean, 1 = highly repetitive)",
            f"- **Fraud / anomaly suspicion score**: `{fraud_score:.3f}`  (0 = clean, 1 = highly suspicious)",
            f"- **Ethics / safety risk score**: `{ethics_score:.3f}`  (0 = low risk, 1 = high risk)",
            f"- **Replicability score**: `{replication_score:.3f}`  (outcome: `{simulated_outcome}`)",
            f"- **Word count**: `{word_count}`  (passes minimum length: `{passes_min_len}`)",
            "",
        )

        # Bias detail
        _add(
            "## Bias & Language\n",
            f"- Emotional language density: `{float(emo['density']):.4f}` (examples: {emo['examples'][:5]})",
            f"- Authority appeals density: `{float(auth['density']):.4f}` (examples: {auth['examples'][:5]})",
            f"- Certainty language density: `{float(cert['density']):.4f}` (examples: {cert['examples'][:5]})",
            "",
        )

        # Stats detail
        _add(
            "## Statistical Rigor\n",
            f"- Has statistical content: `{has_stats}`",
            f"- P-value count: `{int(stats['p_values']['count'])}` (examples: {stats['p_values']['examples']})",
            f"- Confidence interval count: `{int(stats['confidence_intervals']['count'])}` (examples: {stats['confidence_intervals']['examples']})",
            f"- Detected tests: {stats['tests']}",
            f"- Effect size / power terms: {stats['effect_terms']}",
            "",
        )

        # Methodology detail
        _add(
            "## Methodology & Design\n",
            f"- Sample sizes detected: {sample_sizes}",
            f"- Small-sample warning: `{small_sample_warning}`",
            f"- Has control group: `{has_control}`",
            f"- Has randomization: `{has_randomization}`",
            f"- Has preregistration: `{has_preregistration}`",
            f"- Has data sharing: `{has_data_sharing}`",
            "",
        )

        # Replication detail
        _add(
            "## Replicability & Robustness\n",
            f"- Overall replicability score: `{replication_score:.3f}` (simulated outcome: `{simulated_outcome}`)",
            f"- Replication claims: `{bool(claims['has_replication_claims'])}`",
            f"- Robustness: bootstrap=`{bool(robustness['mentions_bootstrap'])}`, "
            f"monte_carlo=`{bool(robustness['mentions_monte_carlo'])}`, "
            f"sensitivity=`{bool(robustness['mentions_sensitivity_analysis'])}`",
            f"- Openness: open_data=`{bool(openness['has_open_data'])}`, "
            f"open_code=`{bool(openness['has_open_code'])}`, "
            f"preregistration=`{bool(openness['has_preregistration'])}`",
            "",
        )

        # Citations detail
        _add(
            "## Citations & References\n",
            f"- Has references section: `{has_ref_section}`",
            f"- Estimated reference count: `{est_ref_count}`",
            f"- DOI count: `{int(citations['doi']['count'])}` (examples: {citations['doi']['examples']})",
            f"- URL count: `{int(citations['urls']['count'])}` (examples: {citations['urls']['examples']})",
            f"- In-text citation count: `{int(citations['in_text_citations']['count'])}` (examples: {citations['in_text_citations']['examples']})",
            f"- Bracket citation count: `{int(citations['bracket_citations']['count'])}` (examples: {citations['bracket_citations']['examples']})",
            f"- Overall citation quality score: `{cit_score:.3f}`",
            "",
        )

        # Plagiarism / redundancy detail
        _add(
            "## Plagiarism / Redundancy Signals\n",
            f"- Overall suspicion score: `{plag_score:.3f}` (0 = clean, 1 = highly repetitive)",
            f"- N-gram repetition ratio (5-grams): `{ngram_rep:.4f}`",
            f"- Repeated sentence ratio: `{sent_rep:.4f}`",
            f"- Top repeated 5-grams: {plag['top_repeated_ngrams']}",
            f"- Top repeated sentences: {plag['top_repeated_sentences']}",
            "",
        )

        # Fraud / anomaly detail
        _add(
            "## Fraud / Anomaly Signals\n",
            f"- Overall fraud / anomaly suspicion score: `{fraud_score:.3f}` (0 = clean, 1 = highly suspicious)",
            f"- Impossible or extreme p-values: `{int(impossible_p['count'])}` (examples: {impossible_p['examples']})",
            f"- p-values clustered just below 0.05: `{int(cluster['count'])}` "
            f"(cluster ratio: `{float(cluster['cluster_ratio']):.4f}`) (examples: {cluster['examples']})",
            f"- Extreme effect language occurrences: `{int(extreme_lang['count'])}` (examples: {extreme_lang['examples']})",
            f"- Suspected mismatched p-text sentences: `{int(mismatch['count'])}` (examples: {mismatch['examples']})",
            "",
        )

        # Ethics / safety detail
        _add(
            "## Ethics & Safety\n",
            f"- Overall ethics / safety risk score: `{ethics_score:.3f}` (0 = low risk, 1 = high risk)",
            f"- Has human subjects: `{has_human_subjects}`",
            f"- Has vulnerable population: `{has_vulnerable}`",
            f"- Mentions ethics approval / IRB: `{has_ethics_approval}`",
            f"- Mentions informed consent: `{has_consent}`",
            f"- Mentions data protection / privacy: `{has_data_protection}`",
            f"- High-risk / dual-use terms: `{int(risk_terms['count'])}` (examples: {risk_terms['examples']})",
            "",
        )

        # Integrity detail
        _add(
            "## Integrity Checks\n",
            f"- Is empty: `{bool(integrity['is_empty'])}`",
            f"- Word count: `{word_count}`",
            f"- Passes minimum word length threshold: `{passes_min_len}`",
            "",
        )

        # Reasoning trace – first few steps
        _add("## Reasoning Trace (first steps)\n")
        for step in trace[:10]:
            ts = step["timestamp"]
            tag = step["tag"]
            desc = step["description"]
            _add(f"- **[{tag}]** `{ts}` – {desc}")
            if step.get("metadata") is not None:
                _add(f"  - metadata: `{step['metadata']}`")
        _add("")

        return "\n".join(lines)

    def save_markdown(self, paper_name: str, result: dict[str, Any]) -> Path:
        md = self.generate_markdown(paper_name, result)
        safe_name = paper_name.replace(" ", "_")
        out_path = self.output_dir / f"{safe_name}_review.md"
        out_path.write_text(md, encoding="utf-8")
        return out_path
