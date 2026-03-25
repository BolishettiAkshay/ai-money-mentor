"""Advisor that turns structured data into personalized financial advice."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from services.fire_engine import calculate_fire_plan
from services.ai.llm_client import call_llm, generate_advice_text
from services.ai.prompt_builder import build_financial_advice_prompt, build_prompt


def _fmt_inr(value: float) -> str:
    """Format a number like INR without needing locale configuration."""
    try:
        # Use Indian-style comma grouping.
        v = int(round(value))
        s = str(abs(v))
        if len(s) > 3:
            last3 = s[-3:]
            rest = s[:-3]
            parts = []
            while len(rest) > 2:
                parts.append(rest[-2:])
                rest = rest[:-2]
            if rest:
                parts.append(rest)
            s = ",".join(reversed(parts)) + "," + last3
        sign = "-" if v < 0 else ""
        # Use ASCII-only currency label to avoid console encoding issues.
        return f"{sign}INR {s}"
    except Exception:
        return f"INR {value}"


def _extract_parts(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Extract (user, metrics, score, fire) from nested or flat inputs."""
    if any(k in data for k in ("user", "metrics", "score", "fire")):
        return data.get("user") or {}, data.get("metrics") or {}, data.get("score") or {}, data.get("fire") or {}

    user = {"age": data.get("age"), "income": data.get("income"), "expenses": data.get("expenses")}
    metrics = {
        "savings_rate": data.get("savings_rate"),
        "emergency_ratio": data.get("emergency_ratio"),
        "dti": data.get("dti"),
        "net_worth": data.get("net_worth"),
    }
    score = {"score": data.get("score"), "score_status": data.get("score_status")}
    fire = data.get("fire_plan") or data.get("fire") or {}
    return user, metrics, score, fire


def _to_float(value: Any) -> float:
    try:
        if value is None or isinstance(value, bool):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any) -> int:
    try:
        if value is None or isinstance(value, bool):
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _fallback_advice_json(data: Dict[str, Any]) -> Dict[str, Any]:
    # Exact fallback requested by the user.
    return {
        "summary": "Your financial health is stable but can improve.",
        "actions": [
            "Increase savings",
            "Reduce unnecessary expenses",
        ],
        "risks": [],
        "opportunities": [],
    }


def _fallback_advice(context: Dict[str, Any]) -> str:
    """Deterministic advice when OpenAI API key is not configured."""
    age = context.get("age")
    income = float(context.get("income") or 0.0)
    expenses = float(context.get("expenses") or 0.0)
    savings_rate = float(context.get("savings_rate") or 0.0)
    emergency_ratio = float(context.get("emergency_ratio") or 0.0)
    dti = float(context.get("dti") or 0.0)
    net_worth = float(context.get("net_worth") or 0.0)

    fire_plan = context.get("fire_plan") or {}
    years_to_fire = int(float(fire_plan.get("years_to_fire") or 0))
    retirement_age = int(float(fire_plan.get("retirement_age") or 0))
    fire_status = str(fire_plan.get("status") or "")
    monthly_investment = float(fire_plan.get("monthly_investment") or 0.0)

    monthly_surplus = max(0.0, income - max(0.0, expenses))
    investment_headroom = max(0.0, monthly_surplus - max(0.0, monthly_investment))

    # Emergency fund: interpret `emergency_ratio` as "months of expenses".
    monthly_expenses = max(0.0, expenses)
    current_emergency = emergency_ratio * monthly_expenses
    target_emergency = 6.0 * monthly_expenses
    emergency_gap = max(0.0, target_emergency - current_emergency)

    score_status = str(context.get("score_status") or "")

    # Summary.
    summary = (
        f"Financial health looks {score_status or 'mixed'}; your FIRE estimate is {fire_status or 'unclear'} "
        f"({years_to_fire} years to FIRE, retirement age ~{retirement_age})."
    )
    if emergency_gap > 0:
        summary += f" Your emergency fund gap is about {_fmt_inr(emergency_gap)}."

    # Steps (exactly 5).
    steps = []
    if emergency_gap > 0:
        steps.append(
            f"Build an emergency fund of ~{_fmt_inr(target_emergency)} by topping up ~{_fmt_inr(emergency_gap)} "
            f"(park in liquid funds/FD ladder)."
        )
    else:
        steps.append("Maintain your 6-month emergency buffer (currently estimated at ~6+ months); avoid investing it in risky assets.")

    if dti >= 0.3:
        steps.append(
            f"Reduce debt pressure: aim to bring DTI below 0.3 by using surplus first for high-interest debt; "
            f"target an EMI reduction or prepayment of ~{_fmt_inr(min(monthly_surplus, expenses * 0.15))} monthly (start small)."
        )
    else:
        steps.append("Keep debt controlled: continue timely EMIs and avoid taking new high-interest debt while you build buffers.")

    if monthly_surplus > 0 and investment_headroom > 0:
        steps.append(
            f"Increase monthly investing by up to ~{_fmt_inr(investment_headroom)} (use SIP). "
            f"Allocate between low-cost index funds and equity funds; keep a portion for debt/ultra-short duration for stability."
        )
    else:
        steps.append(
            "Your monthly surplus is tight. Focus on increasing savings by 5-10% first (expense cuts) before raising SIP."
        )

    # Expense optimization tied to savings rate.
    if savings_rate < 0.25:
        steps.append("Raise savings rate toward 25%: cut non-essential spends by ~5-10% and redirect the amount into SIP on salary day.")
    else:
        steps.append("Sustain your current savings rate; review subscriptions/insurance riders annually to prevent silent expense creep.")

    # Tax-saving (India-specific) with assumptions.
    steps.append(
        "Use India-specific tax saves where eligible: consider `80C` (PF/PPF/ELSS up to limits) and `80CCD(1B)` via NPS; "
        "confirm your exact tax bracket and limits before committing."
    )

    # Risks.
    risks = []
    risks.append("No emergency buffer leads to forced high-interest debt during job/health shocks.")
    if dti >= 0.3:
        risks.append("High DTI/over-leverage can restrict cash flow, delaying both debt cleanup and FIRE contributions.")
    if fire_status == "Not Possible Currently" or years_to_fire == 0 and monthly_investment == 0:
        risks.append("FIRE looks currently not feasible because you cannot invest monthly (or inputs indicate very limited viability).")
    elif years_to_fire > 25:
        risks.append("Late retirement risk: timeline suggests current saving/investing pace is too low for your FIRE target.")
    else:
        risks.append("Execution risk: even with a workable plan, missed SIP months or expense inflation can push retirement beyond your target.")

    improvements = []
    improvements.append(f"Set a monthly target: invest at least ~{_fmt_inr(max(0.0, monthly_investment))} consistently; automate SIPs to avoid leaks.")
    if emergency_gap > 0:
        improvements.append(f"Close the emergency gap first; after ~{_fmt_inr(target_emergency)} is reached, rotate excess from liquid to long-term SIP.")
    if investment_headroom > 0:
        improvements.append(f"Then increase SIP gradually by ~{_fmt_inr(min(investment_headroom, monthly_surplus))} until your savings rate improves.")

    # Keep it concise and in the exact format requested by the prompt builder.
    return (
        f"Summary: {summary}\n"
        "Steps:\n"
        + "\n".join([f"{i + 1}. {s}" for i, s in enumerate(steps[:5])])
        + "\n"
        f"Risks: {risks[0]}{' ' + risks[1] if len(risks) > 1 else ''}"
        + (" " + risks[2] if len(risks) > 2 else "")
        + "\n"
        "Improvements: " + " ".join(improvements[:3])
    )


def generate_financial_advice(context: Dict[str, Any], model: Optional[str] = None) -> str:
    """
    Generate an actionable, concise advice response for an Indian user.

    `context` should include the keys required by `build_financial_advice_prompt`.
    """

    # Populate FIRE plan automatically when the caller provides raw FIRE inputs.
    if not context.get("fire_plan"):
        required = ("age", "expenses", "savings", "monthly_savings")
        if all(k in context for k in required):
            context = dict(context)  # avoid mutating caller's dict
            context["fire_plan"] = calculate_fire_plan(context)

    # Deterministic fallback to ensure we always return actionable structure.
    if not os.environ.get("OPENAI_API_KEY"):
        return _fallback_advice(context)

    prompt = build_financial_advice_prompt(context)
    return generate_advice_text(prompt, model=model)


def generate_advice(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate structured AI advice JSON:
      {summary, actions, risks, opportunities}

    If the API fails, returns deterministic fallback advice.
    """
    # If the caller provided raw FIRE inputs, compute the plan so the LLM has concrete numbers.
    # (Backend computation only; AI must not calculate.)
    if "fire" not in data and "fire_plan" not in data:
        required = ("age", "expenses", "savings", "monthly_savings")
        if all(k in data for k in required):
            data = dict(data)
            data["fire_plan"] = calculate_fire_plan(data)
            data["fire"] = data["fire_plan"]

    prompt = build_prompt(data)

    try:
        return call_llm(prompt)
    except Exception:
        return _fallback_advice_json(data)

