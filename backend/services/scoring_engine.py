"""Financial scoring engine for normalized user financial metrics."""

from __future__ import annotations

from math import isfinite
from typing import Any


def _to_float(value: Any) -> float:
    """Convert a value to finite float, defaulting to 0.0 for invalid values."""
    if isinstance(value, bool):
        return 0.0

    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0

    if not isfinite(number):
        return 0.0
    return number


def _score_emergency_fund(ratio: float) -> int:
    if ratio < 1.0:
        return 5
    if ratio <= 3.0:
        return 10
    if ratio <= 6.0:
        return 15
    return 20


def _score_savings_rate(rate: float) -> int:
    if rate < 0.1:
        return 5
    if rate <= 0.3:
        return 10
    if rate <= 0.5:
        return 15
    return 20


def _score_debt_to_income(ratio: float) -> int:
    if ratio > 0.5:
        return 5
    if ratio >= 0.3:
        return 10
    if ratio >= 0.1:
        return 15
    return 20


def _score_expense_ratio(ratio: float) -> int:
    if ratio > 0.8:
        return 5
    if ratio >= 0.6:
        return 8
    if ratio >= 0.4:
        return 12
    return 15


def _score_net_worth(net_worth: float) -> int:
    if net_worth < 0:
        return 5
    if net_worth <= 100000:
        return 10
    return 15


def _score_investment_capacity(capacity: float) -> int:
    if capacity <= 0:
        return 0
    if capacity < 10000:
        return 5
    return 10


def _status_from_score(score: int) -> str:
    if score < 40:
        return "Poor"
    if score <= 60:
        return "Average"
    if score <= 80:
        return "Good"
    return "Excellent"


def calculate_financial_score(metrics: dict) -> dict:
    """
    Calculate a 0-100 financial score and category breakdown.

    Expected metrics keys:
    - savings_rate
    - emergency_fund_ratio
    - debt_to_income_ratio
    - expense_ratio
    - net_worth
    - investment_capacity
    """
    try:
        payload = metrics if isinstance(metrics, dict) else {}

        savings_rate = _to_float(payload.get("savings_rate"))
        emergency_fund_ratio = _to_float(payload.get("emergency_fund_ratio"))
        debt_to_income_ratio = _to_float(payload.get("debt_to_income_ratio"))
        expense_ratio = _to_float(payload.get("expense_ratio"))
        net_worth_value = _to_float(payload.get("net_worth"))
        investment_capacity = _to_float(payload.get("investment_capacity"))

        breakdown = {
            "emergency_fund": _score_emergency_fund(emergency_fund_ratio),
            "savings": _score_savings_rate(savings_rate),
            "debt": _score_debt_to_income(debt_to_income_ratio),
            "expenses": _score_expense_ratio(expense_ratio),
            "net_worth": _score_net_worth(net_worth_value),
            "investment_capacity": _score_investment_capacity(investment_capacity),
        }

        total_score = int(sum(breakdown.values()))
        total_score = max(0, min(100, total_score))

        return {
            "total_score": total_score,
            "breakdown": breakdown,
            "status": _status_from_score(total_score),
        }
    except Exception:
        return {
            "total_score": 0,
            "breakdown": {
                "emergency_fund": 0,
                "savings": 0,
                "debt": 0,
                "expenses": 0,
                "net_worth": 0,
                "investment_capacity": 0,
            },
            "status": "Poor",
        }
