"""Validation and normalization utilities for financial user input."""

from __future__ import annotations

from math import isfinite
from typing import Any

REQUIRED_FIELDS = ("age", "income", "expenses", "savings", "loans")


def _to_number(value: Any, field_name: str, errors: list[str]) -> float | None:
    """Convert supported values to a finite float, collecting errors when invalid."""
    if isinstance(value, bool):
        errors.append(f"'{field_name}' must be a number, not a boolean.")
        return None

    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        raw = value.strip()
        if raw == "":
            errors.append(f"'{field_name}' is required and cannot be empty.")
            return None
        try:
            number = float(raw)
        except ValueError:
            errors.append(f"'{field_name}' must be a numeric value.")
            return None
    else:
        errors.append(
            f"'{field_name}' must be an int, float, or numeric string."
        )
        return None

    if not isfinite(number):
        errors.append(f"'{field_name}' must be a finite number.")
        return None

    return number


def _missing_required_fields(data: dict[str, Any]) -> list[str]:
    """Return a list of fields that are missing from input data."""
    return [field for field in REQUIRED_FIELDS if field not in data]


def _validate_ranges(values: dict[str, float], errors: list[str]) -> int | None:
    """Validate field-level numeric constraints and return normalized age."""
    age_raw = values["age"]
    if not age_raw.is_integer():
        errors.append("'age' must be a whole number between 18 and 80.")
        age = None
    else:
        age = int(age_raw)
        if not 18 <= age <= 80:
            errors.append("'age' must be between 18 and 80.")

    if values["income"] <= 0:
        errors.append("'income' must be greater than 0.")
    if values["expenses"] < 0:
        errors.append("'expenses' cannot be negative.")
    if values["savings"] < 0:
        errors.append("'savings' cannot be negative.")
    if values["loans"] < 0:
        errors.append("'loans' cannot be negative.")

    return age


def validate_and_normalize(data: dict) -> dict:
    """
    Validate and normalize user financial input.

    Returns:
    - {"status": "success", "data": {...}} when valid
    - {"status": "error", "errors": [...]} when invalid
    """
    try:
        if not isinstance(data, dict):
            return {
                "status": "error",
                "errors": ["Input payload must be a dictionary."],
            }

        errors: list[str] = []
        missing_fields = _missing_required_fields(data)
        if missing_fields:
            return {
                "status": "error",
                "errors": [
                    f"Missing required field: '{field}'." for field in missing_fields
                ],
            }

        parsed_values: dict[str, float] = {}
        for field in REQUIRED_FIELDS:
            parsed = _to_number(data.get(field), field, errors)
            if parsed is not None:
                parsed_values[field] = parsed

        if len(parsed_values) != len(REQUIRED_FIELDS):
            return {"status": "error", "errors": errors}

        age = _validate_ranges(parsed_values, errors)
        if errors or age is None:
            return {"status": "error", "errors": errors}

        income = parsed_values["income"]
        expenses = parsed_values["expenses"]

        # Negative monthly savings are clamped to 0 for safety.
        monthly_savings = max(income - expenses, 0.0)
        savings_rate = max(monthly_savings / income, 0.0) if income > 0 else 0.0

        normalized_data = {
            "age": age,
            "income": income,
            "expenses": expenses,
            "savings": parsed_values["savings"],
            "loans": parsed_values["loans"],
            "monthly_savings": monthly_savings,
            "savings_rate": savings_rate,
        }

        return {"status": "success", "data": normalized_data}
    except Exception as exc:  # Defensive guardrail to prevent hard crashes.
        return {
            "status": "error",
            "errors": [f"Unexpected validation error: {exc}"],
        }
