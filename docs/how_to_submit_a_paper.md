# How to Submit a Paper to Nobias

## Via Dashboard (Recommended)
1. Open http://localhost:8501
2. Upload PDF or paste text
3. Optional: Add paper name
4. Click "Review Paper"
5. View full report with trust score, verdict, and self-audit

## Via API
```bash
curl -X POST "http://localhost:8000/submission/submit" \
     -H "X-API-Key: nobias-secret-key-2025" \
     -F "file=@my_paper.pdf"