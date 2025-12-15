# Nobias AI Peer Review — Architecture Overview

**Date**: December 15, 2025  
**Version**: 1.0

Nobias is a fully open-source, deterministic, self-auditing framework designed to replace the flawed human peer-review system with transparent, evidence-only evaluation.

## Core Principles
- Content-only evaluation (blind to author/institution)
- Full reasoning trace for every decision
- Real-time self-auditing for hallucinations/overconfidence
- Uncertainty propagation with confidence intervals
- Replicability as a first-class metric
- No suppression of rigorous anomalous results

## High-Level Architecture

Ingestion → Core Analysis → Self-Audit → Verdict → Report
↑          ↑            ↑         ↑        ↓
Config     Ethics      Hallucination  API    Dashboard
Guard


### Key Modules
- **Core/**: 10+ heuristic engines (bias, stats, methodology, fraud, ethics, replication, etc.)
- **Ai_Models/**: Hallucination detector + future symbolic models
- **Evaluation/**: Scoring system with uncertainty propagation
- **API/**: Modular FastAPI service (secure, rate-limited)
- **UI/dashboard/**: Streamlit interactive front-end
- **Ethics/**: Non-negotiable guardrails and manifesto
- **Config/**: YAML-based tunable parameters

## Data Flow
1. PDF/text → Advanced ingestion (PyMuPDF)
2. Parallel analysis by all engines
3. HallucinationGuard self-audits outputs
4. FinalVerdictEngine produces trust score ± uncertainty
5. ReportGenerator creates human-readable Markdown
6. Served via API or interactive dashboard

## Revolutionary Features
- First system to prove it is not hallucinating
- Uncertainty-aware scoring (trust ± std dev, 95% CI)
- Protection for anomalous but rigorous research
- Fully reproducible (no LLMs in analysis path)

Nobias is not reform.  
Nobias is replacement.