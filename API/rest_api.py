# API/rest_api.py
from __future__ import annotations

from fastapi import FastAPI

from API.submission_endpoints import router as submission_router
from API.evaluation_endpoints import router as evaluation_router
from API.reviewer_endpoints import router as reviewer_router

app = FastAPI(
    title="Nobias AI Peer Review API",
    description="Transparent, incorruptible, self-auditing scientific peer review.",
    version="1.0.0",
    contact={"name": "Youssef"},
    license_info={"name": "MIT"},
)

# Include modular routers
app.include_router(submission_router, prefix="/submission", tags=["Submission"])
app.include_router(evaluation_router, prefix="/evaluation", tags=["Evaluation"])
app.include_router(reviewer_router, prefix="/reviewer", tags=["Reviewer"])

@app.get("/")
async def root():
    return {
        "message": "Nobias AI Peer Review API",
        "docs": "/docs",
        "endpoints": {
            "submit": "/submission/submit",
            "reports": "/evaluation/reports",
            "list_reports": "/evaluation/reports",
        },
    }