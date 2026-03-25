"""Compute financial metrics used by the scoring engine."""

from __future__ import annotations

from typing import Any, Dict


def _to_float(value: Any) -> float:
    try:
        if value is None or isinstance(value, bool):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def calculate_financial_metrics(validated_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate the metrics required by `backend/services/scoring_engine.py`.

    Expected scoring_engine keys:
    - savings_rate
    - emergency_fund_ratio
    - debt_to_income_ratio
    - expense_ratio
    - net_worth
    - investment_capacity
    """
    income = max(0.0, _to_float(validated_data.get("income")))
    expenses = max(0.0, _to_float(validated_data.get("expenses")))
    savings = max(0.0, _to_float(validated_data.get("savings")))
    loans = max(0.0, _to_float(validated_data.get("loans")))
    monthly_savings = max(0.0, _to_float(validated_data.get("monthly_savings")))

    # Monthly savings rate.
    savings_rate = (monthly_savings / income) if income > 0 else 0.0

    # Emergency fund ratio treated as "months of expenses covered" by current savings.
    # If expenses are 0, there is no meaningful ratio.
    emergency_fund_ratio = (savings / expenses) if expenses > 0 else 0.0

    # Debt-to-income ratio. Interpret `loans` as monthly debt burden (EMIs).
    debt_to_income_ratio = (loans / income) if income > 0 else 0.0

    expense_ratio = (expenses / income) if income > 0 else 0.0

    # Approximate net worth: savings minus outstanding debt.
    net_worth = savings - loans

    # Investment capacity: how much can be invested monthly.
    investment_capacity = monthly_savings

    return {
        "savings_rate": float(savings_rate),
        "emergency_fund_ratio": float(emergency_fund_ratio),
        "debt_to_income_ratio": float(debt_to_income_ratio),
        "expense_ratio": float(expense_ratio),
        "net_worth": float(net_worth),
        "investment_capacity": float(investment_capacity),
    }

