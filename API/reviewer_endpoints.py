# API/reviewer_endpoints.py
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# Future reviewer-facing endpoints
# e.g., flag claims, add comments, vote on replicability


@router.get("/health")
async def reviewer_health():
    return {"status": "reviewer endpoints ready for future implementation"}