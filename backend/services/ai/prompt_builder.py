"""Prompt builder for AI-based financial advisory (India-specific, structured output)."""

from __future__ import annotations

from typing import Any, Dict, Tuple


def _to_float(value: Any) -> float:
    """Best-effort numeric coercion (invalid/missing -> 0.0)."""
    try:
        if value is None or isinstance(value, bool):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_int(value: Any) -> int:
    try:
        if value is None or isinstance(value, bool):
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _extract_parts(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Extract (user, metrics, score, fire) from either:
    - nested input: {user, metrics, score, fire}
    - flat input: {age, income, expenses, savings_rate, ...}
    """
    if any(k in data for k in ("user", "metrics", "score", "fire")):
        user = data.get("user") or {}
        metrics = data.get("metrics") or {}
        score = data.get("score") or {}
        fire = data.get("fire") or {}
        return user, metrics, score, fire

    user = {
        "age": data.get("age"),
        "income": data.get("income"),
        "expenses": data.get("expenses"),
    }
    metrics = {
        "savings_rate": data.get("savings_rate"),
        "emergency_ratio": data.get("emergency_ratio"),
        "dti": data.get("dti"),
        "net_worth": data.get("net_worth"),
    }
    score = {
        "score": data.get("score"),
        "score_status": data.get("score_status"),
        "status": data.get("score_status"),
        "total_score": data.get("score"),
    }
    # Allow either `fire_plan` or `fire`.
    fire = data.get("fire_plan") or data.get("fire") or {}
    return user, metrics, score, fire


def build_prompt(data: Dict[str, Any]) -> str:
    """
    Takes user + metrics + score + fire data and returns a formatted prompt string.

    `data` can be nested or flat. See `_extract_parts()` for supported keys.
    """

    user, metrics, score, fire = _extract_parts(data)

    age = _as_int(user.get("age"))
    income = _to_float(user.get("income"))
    expenses = _to_float(user.get("expenses"))

    savings_rate = _to_float(metrics.get("savings_rate"))
    emergency_ratio = _to_float(metrics.get("emergency_ratio"))
    dti = _to_float(metrics.get("dti"))
    net_worth = _to_float(metrics.get("net_worth"))

    score_value = _as_int(score.get("score", score.get("total_score")))
    score_status = str(score.get("score_status") or score.get("status") or "")

    years_to_fire = _as_int(fire.get("years_to_fire", fire.get("years_to_retirement")))
    retirement_age = _as_int(fire.get("retirement_age"))
    fire_status = str(fire.get("status") or "")
    monthly_investment = _to_float(fire.get("monthly_investment"))

    # Backend-derived figures for specificity (AI must NOT calculate anything).
    monthly_expenses = max(0.0, expenses)
    current_emergency_fund = max(0.0, emergency_ratio) * monthly_expenses  # ratio treated as months-of-expenses
    target_emergency_fund = 6.0 * monthly_expenses
    emergency_gap = max(0.0, target_emergency_fund - current_emergency_fund)

    # Prefer `monthly_investment` if present; otherwise approximate from savings_rate.
    monthly_savings_current = monthly_investment if monthly_investment > 0 else savings_rate * max(0.0, income)
    target_savings_rate = 0.25
    target_monthly_savings = target_savings_rate * max(0.0, income)
    sip_increase_headroom = max(0.0, target_monthly_savings - monthly_savings_current)

    return (
        "You are a personal finance advisor for Indian users.\n"
        "Convert the provided numbers into concise, practical, India-specific advice.\n\n"
        "IMPORTANT: Do not do any calculations or simulations. Use the numbers exactly as provided below.\n\n"
        "User:\n"
        f"- Age: {age}\n"
        f"- Monthly Income (INR): {income}\n"
        f"- Monthly Expenses (INR): {expenses}\n\n"
        "Metrics:\n"
        f"- Savings Rate: {savings_rate}\n"
        f"- Emergency Fund Ratio (months of expenses): {emergency_ratio}\n"
        f"- Debt-to-Income Ratio (DTI): {dti}\n"
        f"- Net Worth (INR): {net_worth}\n\n"
        "Score:\n"
        f"- Score: {score_value}\n"
        f"- Status: {score_status}\n\n"
        "FIRE Plan (backend computed):\n"
        f"- Years to Retirement: {years_to_fire}\n"
        f"- Retirement Age: {retirement_age}\n"
        f"- Status: {fire_status}\n"
        f"- Current Monthly Investment (INR): {monthly_investment}\n\n"
        "Backend-derived figures (use these; do NOT calculate):\n"
        f"- Current Emergency Fund Estimate (INR): {current_emergency_fund}\n"
        f"- Target Emergency Fund (INR, 6 months): {target_emergency_fund}\n"
        f"- Emergency Fund Gap (INR): {emergency_gap}\n"
        f"- Estimated Monthly Savings Current (INR): {monthly_savings_current}\n"
        f"- Target Monthly Savings at 25% Savings Rate (INR): {target_monthly_savings}\n"
        f"- SIP Increase Headroom to reach 25% (INR): {sip_increase_headroom}\n\n"
        "Responsibilities:\n"
        "1. Generate Financial Summary (short, 2-3 lines max).\n"
        "2. Identify Weak Areas (tie to metrics).\n"
        "3. Generate Actionable Steps (MOST IMPORTANT): exactly 5 steps, each concrete and specific.\n"
        "4. Highlight Risks (at least 2, tied to emergency buffer, DTI, and FIRE timeline).\n"
        "5. Suggest Opportunities (India-specific instruments/tax options).\n\n"
        "Output Requirements:\n"
        "Return ONLY a valid JSON object with exactly these keys:\n"
        "- summary: string\n"
        "- actions: array of exactly 5 strings\n"
        "- risks: array of strings (2-5 items)\n"
        "- opportunities: array of strings (2-5 items)\n\n"
        "Formatting rules:\n"
        "- India-specific only (INR amounts, PF/PPF/EPF, NPS, ELSS, index funds/SIPs where relevant).\n"
        "- No generic advice. If a key value is 0 or unknown, the advice must explicitly say what to measure/verify.\n"
        "- Do not include any other text besides the JSON.\n"
    )


# Backward compatible alias (older name used earlier in this codebase).
def build_financial_advice_prompt(context: Dict[str, Any]) -> str:
    return build_prompt(context)

