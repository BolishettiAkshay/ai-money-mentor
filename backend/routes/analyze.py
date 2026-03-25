"""FastAPI route for financial analysis."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services.orchestrator import run_financial_analysis

router = APIRouter()


@router.post("/analyze")
def analyze_finances(data: dict):
    result = run_financial_analysis(data)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

