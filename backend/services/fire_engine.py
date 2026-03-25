"""FIRE (Financial Independence Retire Early) planning utilities."""

from __future__ import annotations

from math import isfinite
from typing import Any


def _to_finite_float(value: Any) -> float:
    """Convert `value` to a finite float, defaulting to 0.0 for invalid inputs."""
    if isinstance(value, bool):
        return 0.0

    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0

    if not isfinite(number):
        return 0.0
    return number


def calculate_fire_plan(data: dict) -> dict:
    """
    Calculate a FIRE plan based on a conservative fixed return simulation.

    Expected keys in `data`:
    - age
    - income
    - expenses
    - savings
    - monthly_savings
    """

    payload = data if isinstance(data, dict) else {}

    age = _to_finite_float(payload.get("age"))
    age_int = max(0, int(age))

    income = _to_finite_float(payload.get("income"))
    expenses = _to_finite_float(payload.get("expenses"))
    savings = _to_finite_float(payload.get("savings"))
    monthly_savings = _to_finite_float(payload.get("monthly_savings"))

    # Guardrails / assumptions.
    fire_multiple = 25
    annual_return = 0.10
    max_years = 60

    annual_expenses = max(0.0, expenses) * 12.0
    fire_corpus = annual_expenses * fire_multiple

    # Edge case: if the user cannot (or will not) invest, plan is not possible.
    monthly_investment = max(0.0, monthly_savings)
    if monthly_investment == 0.0:
        return {
            "fire_corpus": float(fire_corpus),
            "years_to_fire": 0,
            "retirement_age": age_int,
            "monthly_investment": float(monthly_investment),
            "status": "Not Possible Currently",
        }

    # Edge case: unrealistic inputs where income cannot reasonably cover expenses.
    # (We treat this as not viable for planning purposes.)
    if income <= 0.0 or income < max(0.0, expenses):
        return {
            "fire_corpus": float(fire_corpus),
            "years_to_fire": 0,
            "retirement_age": age_int,
            "monthly_investment": float(monthly_investment),
            "status": "Not Possible Currently",
        }

    # If expenses are 0 (or negative after sanitization), the FIRE corpus is 0.
    # In that case, they are effectively already "there".
    if fire_corpus <= 0.0:
        return {
            "fire_corpus": float(fire_corpus),
            "years_to_fire": 0,
            "retirement_age": age_int,
            "monthly_investment": float(monthly_investment),
            "status": "Excellent",
        }

    # 2. Simulate wealth growth.
    total = max(0.0, savings)
    if total >= fire_corpus:
        years_to_fire = 0
    else:
        years_to_fire = max_years  # cap ensures no infinite loops
        for year in range(1, max_years + 1):
            total = total * (1.0 + annual_return) + (monthly_investment * 12.0)
            if total >= fire_corpus:
                years_to_fire = year
                break

    # 3. Compute retirement age.
    retirement_age = age_int + years_to_fire

    # 5. Status based on time-to-FIRE.
    if years_to_fire <= 15:
        status = "Excellent"
    elif years_to_fire <= 25:
        status = "On Track"
    else:
        status = "Needs Improvement"

    # 6. Return required shape.
    return {
        "fire_corpus": float(fire_corpus),
        "years_to_fire": int(years_to_fire),
        "retirement_age": int(retirement_age),
        "monthly_investment": float(monthly_investment),
        "status": status,
    }

