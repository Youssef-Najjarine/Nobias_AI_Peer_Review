# Nobias AI Peer Review API Documentation

**Base URL**: `http://localhost:8000`  
**Docs**: `/docs` (Swagger) | `/redoc`

## Authentication
- Header: `X-API-Key: nobias-secret-key-2025`

## Endpoints

### Submission
- **POST** `/submission/submit`
  - Submit paper via file upload or text
  - Returns verdict, report URL, hallucination audit

### Evaluation
- **GET** `/evaluation/reports/{filename}` — Download report
- **GET** `/evaluation/reports` — List all reports

### Reviewer (Future)
- Reserved for claim-flagging and feedback tools

## Response Example
```json
{
  "paper_name": "quantum_breakthrough.pdf",
  "final_verdict": {
    "overall_trust_score": 0.82,
    "trust_std_dev": 0.09,
    "trust_95_confidence_interval": [0.64, 1.00],
    "verdict_label": "Reliable"
  },
  "hallucination_audit": {
    "overall_hallucination_risk": 0.12,
    "passed_all_audits": true
  },
  "report_url": "/evaluation/reports/quantum_breakthrough_review.md"
}

Rate limit: 10 requests/minute per IP


### docs/scoring_system_explained.md
```markdown
# Nobias Scoring System — Explained

Nobias evaluates papers across 8 weighted dimensions:

| Component      | Weight | Inverted? | Uncertainty Heuristic |
|----------------|--------|-----------|------------------------|
| Statistics     | 0.18   | No        | Low if strong tests, high if absent |
| Methodology    | 0.18   | No        | Low if randomized/controls, high otherwise |
| Replication    | 0.14   | No        | Low if open data/code, high if closed |
| Citations      | 0.12   | No        | Low if DOIs/references, high if weak |
| Bias           | 0.08   | Yes       | Fixed moderate (language noisy) |
| Plagiarism     | 0.10   | Yes       | Moderate |
| Fraud          | 0.10   | Yes       | High if p-hacking signals |
| Ethics         | 0.10   | Yes       | Moderate-high |

**Final Trust Score** = Weighted sum (0.00–1.00)

**Uncertainty** = Propagated variance → std dev → 95% CI

**Verdict Thresholds**
- ≥0.70 → Reliable
- 0.40–0.69 → Mixed
- <0.40 → High Risk

**Hard Overrides** downgrade verdict on high fraud/ethics signals.

Uncertainty ensures honesty: weak evidence → wide CI → cautious interpretation.