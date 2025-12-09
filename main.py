# main.py

from Core.review_engine import ReviewEngine


def main():
    sample_text = """
    This groundbreaking and unprecedented study clearly proves our theory.
    The renowned and prestigious group behind this work comes from elite institutions.
    It is obvious that the results are robust.

    We conducted a randomized controlled experiment with a treatment and control group.
    Participants were randomly assigned to conditions and the study was double-blind.
    The sample size was n = 120 in the treatment group and n = 118 in the control group.

    We conducted a series of t-tests and a one-way ANOVA.
    The main effect was significant (p < 0.01), with several follow-up tests
    also significant (p = 0.032, p <= 0.045).
    A 95% CI [1.2, 2.3] was computed for the primary effect size.
    We additionally report Cohen's d as a standardized effect size and
    performed a power analysis to confirm adequate statistical power.

    The protocol was preregistered on OSF.io and the anonymized data
    are available in a public repository.
    """

    engine = ReviewEngine()
    result = engine.review_paper(sample_text)

    print("=== INTEGRITY RESULT ===")
    print(result["integrity"])

    print("\n=== BIAS RESULT (summary) ===")
    print(f"Overall bias score: {result['bias']['overall_bias_score']:.4f}")

    print("\n=== STATISTICAL RESULT (summary) ===")
    stats = result["statistics"]
    print(f"Has statistical content: {stats['has_statistical_content']}")
    print(f"P-value count: {stats['p_values']['count']}")
    print(f"Rigor score: {stats['overall_rigor_score']:.4f}")

    print("\n=== METHODOLOGY RESULT (summary) ===")
    meth = result["methodology"]
    print(f"Methodology score: {meth['overall_methodology_score']:.4f}")
    print("Sample sizes:", meth["sample_size"]["values"])
    print("Small-sample warning:", meth["sample_size"]["small_sample_warning"])
    print("Has control group:", meth["control_and_blinding"]["has_control_group"])
    print("Has randomization:", meth["design"]["has_randomization"])
    print("Has preregistration:", meth["transparency"]["has_preregistration"])
    print("Has data sharing:", meth["transparency"]["has_data_sharing"])

    print("\n=== REASONING TRACE ===")
    for step in result["trace"]:
        print(f"[{step['timestamp']}] {step['tag']}: {step['description']}")
        if step.get("metadata"):
            print("  metadata:", step["metadata"])


if __name__ == "__main__":
    main()
