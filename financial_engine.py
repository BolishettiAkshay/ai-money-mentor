"""Financial metrics calculation utilities."""

from __future__ import annotations

from math import isfinite
from typing import Any


def _zero_metrics() -> dict[str, float]:
    """Return a default metrics payload with safe zero values."""
    return {
        "savings_rate": 0.0,
        "emergency_fund_ratio": 0.0,
        "debt_to_income_ratio": 0.0,
        "monthly_debt_ratio": 0.0,
        "net_worth": 0.0,
        "expense_ratio": 0.0,
        "investment_capacity": 0.0,
    }


def _to_float(value: Any) -> float:
    """Best-effort conversion to finite float, falling back to 0.0."""
    if isinstance(value, bool):
        return 0.0

    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0

    if not isfinite(number):
        return 0.0
    return number


def _safe_divide(numerator: float, denominator: float) -> float:
    """Safely divide two numbers and return 0.0 when division is invalid."""
    if denominator == 0.0:
        return 0.0

    try:
        value = numerator / denominator
    except Exception:
        return 0.0

    if not isfinite(value):
        return 0.0
    return float(value)


def calculate_financial_metrics(data: dict) -> dict:
    """
    Calculate core financial metrics from validated user financial data.

    Expected keys in `data`:
    age, income, expenses, savings, loans, monthly_savings, savings_rate
    """
    try:
        payload = data if isinstance(data, dict) else {}

        income = _to_float(payload.get("income"))
        expenses = _to_float(payload.get("expenses"))
        savings = _to_float(payload.get("savings"))
        loans = _to_float(payload.get("loans"))
        monthly_savings = _to_float(payload.get("monthly_savings"))

        savings_rate = _safe_divide(monthly_savings, income)
        emergency_fund_ratio = _safe_divide(savings, expenses)
        debt_to_income_ratio = _safe_divide(loans, income * 12.0)
        monthly_debt_ratio = _safe_divide(loans, income)
        net_worth = savings - loans
        expense_ratio = _safe_divide(expenses, income)
        investment_capacity = float(monthly_savings)

        return {
            "savings_rate": float(savings_rate),
            "emergency_fund_ratio": float(emergency_fund_ratio),
            "debt_to_income_ratio": float(debt_to_income_ratio),
            "monthly_debt_ratio": float(monthly_debt_ratio),
            "net_worth": net_worth,
            "expense_ratio": float(expense_ratio),
            "investment_capacity": float(investment_capacity),
        }
    except Exception:
        # Defensive fallback to guarantee no-crash behavior.
        return _zero_metrics()
