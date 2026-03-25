"""Validate and normalize user input for the financial analysis pipeline."""

from __future__ import annotations

from typing import Any, Dict


def _to_non_negative_float(value: Any) -> float:
    try:
        if value is None or isinstance(value, bool):
            return 0.0
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number < 0:
        return 0.0
    return number


def _to_non_negative_int(value: Any) -> int:
    try:
        if value is None or isinstance(value, bool):
            return 0
        number = int(float(value))
    except (TypeError, ValueError):
        return 0
    if number < 0:
        return 0
    return number


def validate_and_normalize(data: dict) -> dict:
    """
    Validate expected keys and normalize them to numeric types.

    Input expected:
    {
      age, income, expenses, savings, loans
    }
    """
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object.")

    required = ("age", "income", "expenses", "savings", "loans")
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    age = _to_non_negative_int(data.get("age"))
    income = _to_non_negative_float(data.get("income"))
    expenses = _to_non_negative_float(data.get("expenses"))
    savings = _to_non_negative_float(data.get("savings"))
    loans = _to_non_negative_float(data.get("loans"))

    # Monthly savings/investment capacity used by FIRE simulation and metrics.
    monthly_savings = max(0.0, income - expenses)

    return {
        "age": age,
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "loans": loans,
        "monthly_savings": monthly_savings,
    }

