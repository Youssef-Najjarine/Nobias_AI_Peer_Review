# API/submission_endpoints.py
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends, Request, status

from API.rate_limiter import limiter
from API.authentication.api_key_auth import get_api_key
from API.schemas import ReviewResponse

from Core.review_engine import ReviewEngine
from Core.report_generator import ReportGenerator
from Core.ingestion.ingestor import DocumentIngestor

router = APIRouter()

engine = ReviewEngine()
report_generator = ReportGenerator(output_dir="reports")
ingestor = DocumentIngestor()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post(
    "/submit",
    response_model=ReviewResponse,
    summary="Submit a paper for review",
    dependencies=[Depends(get_api_key)],
)
@limiter.limit("10/minute")
async def submit_paper(
    request: Request,
    file: Annotated[UploadFile | None, File(description="PDF or text file")] = None,
    text: Annotated[str | None, Form(description="Raw text alternative")] = None,
    paper_name: Annotated[str | None, Form(description="Custom paper name")] = None,
):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Either 'file' or 'text' required.")
    if file and text:
        raise HTTPException(status_code=400, detail="Provide only one of 'file' or 'text'.")

    name = paper_name or (file.filename if file else "unnamed_paper")

    try:
        if file:
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            doc = ingestor.ingest(file_path)
            result = engine.review_paper(doc)
        else:
            result = engine.review_paper(text or "")

        report_path = report_generator.save_markdown(name, result)

        verdict = result["final_verdict"]
        hallucination = result["hallucination_audit"]

        return ReviewResponse(
            paper_name=name,
            status="review_complete",
            final_verdict=verdict,
            hallucination_audit=hallucination,
            report_url=f"/reports/{report_path.name}",
            full_result=None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")