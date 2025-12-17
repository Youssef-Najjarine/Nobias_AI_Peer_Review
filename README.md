# Nobias AI Peer Review

**A Transparent, Incorruptible, Self-Auditing Scientific Peer Review System**

**Date**: December 16, 2025  
**Author**: Youssef Najjarine  
**License**: MIT

## The Problem

Traditional peer review is broken:

- Slow and opaque
- Biased by prestige, institution, and personal networks
- Vulnerable to fraud and p-hacking
- Suppresses rigorous but unconventional research
- No systematic replicability checks
- Human reviewers can hallucinate or overclaim

## The Solution: Nobias

Nobias is a **fully deterministic, open-source, self-auditing** peer review engine that evaluates **only the content** of a paper.

No author names. No institutions. No politics.

Only evidence matters.

### Revolutionary Features
- **Blind Evaluation**: Author/institution data ignored
- **Self-Auditing**: Detects overconfidence, contradictions, and hallucinations in its own analysis
- **Uncertainty Propagation**: Trust score with 95% confidence interval
- **Replicability First**: Heavy weighting for open data/code and robustness
- **Ethics & Integrity Built-In**: Fraud, plagiarism, bias, and ethics checks
- **Full Reasoning Trace**: Every decision fully explained
- **Production-Ready**: FastAPI service + Streamlit dashboard + Docker

## Quick Start

### 1. Local (Docker — Recommended)
```bash
git clone https://github.com/Youssef-Najjarine/Nobias_AI_Peer_Review.git
cd Nobias_AI_Peer_Review
docker build -t nobias .
docker run -p 8000:8000 -p 8501:8501 nobias
exit 0
```
**API**: http://localhost:8000/docs

**Dashboard**: http://localhost:8501
### 2. Local (Native)
```bash
pip install -r requirements.txt
# Run API
python run_api.py

# Run Dashboard
streamlit run UI/dashboard/peer_review_dashboard.py
```
## Project Structure
- **Core/**: 10 heuristic analysis engines
- **Ai_Models/**: Hallucination detector + future extensions
- **API/**: Modular, secure FastAPI service
- **UI/dashboard/**: Interactive Streamlit front-end
- **Ethics/**: Non-negotiable guardrails and manifesto
- **Config/**: YAML-based tunable parameters
- **docs/**: Full documentation
- **Security/**: Encryption, sandbox, tamper detection, audit logging

## Philosophy

> "Science must be judged by evidence alone."

Nobias removes gatekeeping and replaces it with **provable integrity**.

It is not reform.  
It is **replacement**.

## License

MIT — free to use, modify, and deploy.

## Contact

Youssef Najjarine  
GitHub: [@Youssef-Najjarine](https://github.com/Youssef-Najjarine)

---

**Nobias AI Peer Review — December 16, 2025**  
**The future of science is content-only.**