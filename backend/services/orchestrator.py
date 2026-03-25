"""Central orchestrator pipeline: validate -> metrics -> score -> FIRE -> AI."""

from __future__ import annotations

from typing import Any, Dict

from utils.validator import validate_and_normalize
from services.financial_engine import calculate_financial_metrics
from services.scoring_engine import calculate_financial_score
from services.fire_engine import calculate_fire_plan
from services.ai.advisor import generate_advice


def run_financial_analysis(data: dict) -> dict:
    """
    Run end-to-end financial analysis.

    Returns either:
    - {"status": "error", "message": "..."}
    - {"status": "success", "data": {...}}
    """
    try:
        validated = validate_and_normalize(data)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    metrics = calculate_financial_metrics(validated)
    score = calculate_financial_score(metrics)
    fire = calculate_fire_plan(
        {
            "age": validated.get("age"),
            "income": validated.get("income"),
            "expenses": validated.get("expenses"),
            "savings": validated.get("savings"),
            "monthly_savings": validated.get("monthly_savings"),
        }
    )

    # If AI fails, still return other results.
    try:
        advice = generate_advice(
            {
                "user": validated,
                "metrics": metrics,
                "score": score,
                "fire": fire,
            }
        )
    except Exception:
        advice = {
            "summary": "Your financial health is stable but can improve.",
            "actions": ["Increase savings", "Reduce unnecessary expenses"],
            "risks": [],
            "opportunities": [],
        }

    return {
        "status": "success",
        "data": {
            "user_data": validated,
            "metrics": metrics,
            "score": score,
            "fire": fire,
            "advice": advice,
        },
    }

