# API/evaluation_endpoints.py
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


@router.get("/reports/{filename}")
async def get_report(filename: str):
    path = REPORT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path=path, media_type="text/markdown", filename=filename)


@router.get("/reports")
async def list_reports():
    reports = [f.name for f in REPORT_DIR.iterdir() if f.suffix == ".md"]
    return {"reports": sorted(reports, reverse=True), "count": len(reports)}