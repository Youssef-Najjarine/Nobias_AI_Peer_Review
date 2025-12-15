# Nobias Scoring System — Explained

Nobias evaluates papers across 8 weighted dimensions (configurable in Config/scoring_weights.yaml):

| Component      | Weight | Inverted? | Key Signals |
|----------------|--------|-----------|-------------|
| Statistics     | 0.18   | No        | p-values, CIs, tests, effect sizes |
| Methodology    | 0.18   | No        | Design, sample size, controls, preregistration |
| Replication    | 0.14   | No        | Open data/code, robustness checks |
| Citations      | 0.12   | No        | References section, DOIs, in-text citations |
| Bias           | 0.08   | Yes       | Emotional/authority/certainty language |
| Plagiarism     | 0.10   | Yes       | N-gram/sentence redundancy |
| Fraud          | 0.10   | Yes       | p-hacking, impossible values, extreme claims |
| Ethics         | 0.10   | Yes       | Human subjects, dual-use, consent mentions |

**Final Trust Score** = Weighted sum (0.00–1.00)

**Uncertainty Propagation**
- Each component has heuristic uncertainty (lower for strong signals)
- Variance propagated → std dev → 95% confidence interval
- Displayed as: `trust ± std_dev (95% CI: lower–upper)`

**Verdict Thresholds**
- ≥0.70 → Reliable
- 0.40–0.69 → Mixed
- <0.40 → High Risk

**Hard Overrides** force "High Risk" on severe fraud/ethics signals.

Uncertainty ensures intellectual honesty: weak evidence → wide CI → cautious verdict.