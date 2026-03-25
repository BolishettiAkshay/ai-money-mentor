"""LLM client wrapper for structured financial advice (provider-swap friendly)."""

from __future__ import annotations

import os
import json
from typing import Any, Dict, Optional

try:
    # OpenAI Python SDK (2.x).
    from openai import OpenAI
except Exception:  # pragma: no cover - environment may not have openai
    OpenAI = None  # type: ignore[assignment]

def _json_schema() -> Dict[str, Any]:
    return {
        "name": "financial_advice",
        "description": "Structured financial advice for Indian users.",
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "summary": {"type": "string"},
                "actions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "risks": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "opportunities": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["summary", "actions", "risks", "opportunities"],
        },
        "strict": True,
    }


def call_llm(prompt: str) -> Dict[str, Any]:
    """
    Calls the LLM provider and returns structured JSON output:
    {summary, actions, risks, opportunities}.

    Raises an exception on failures so the caller can handle fallback.
    """

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        raise RuntimeError("OPENAI_API_KEY is not set or OpenAI SDK is unavailable.")

    chosen_model = os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    client = OpenAI(api_key=api_key)

    resp = client.responses.create(
        model=chosen_model,
        input=prompt,
        # Enforce structured output from the model.
        text={
            "format": {
                "type": "json_schema",
                "json_schema": _json_schema(),
            }
        },
        temperature=0.2,
        max_output_tokens=800,
    )

    raw = getattr(resp, "output_text", "") or ""
    raw = raw.strip()
    if not raw:
        raise RuntimeError("LLM returned empty output.")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"LLM returned non-JSON output: {e}") from e

    # Minimal validation.
    for k in ("summary", "actions", "risks", "opportunities"):
        if k not in parsed:
            raise RuntimeError(f"LLM JSON missing key: {k}")

    if not isinstance(parsed["actions"], list) or not isinstance(parsed["risks"], list) or not isinstance(parsed["opportunities"], list):
        raise RuntimeError("LLM JSON fields have invalid types.")

    return parsed


def generate_advice_text(prompt: str, *, model: Optional[str] = None, temperature: float = 0.2, max_output_tokens: int = 600) -> str:
    """
    Backward-compatible helper for older code paths.

    Returns the `summary` string extracted from the structured JSON.
    """

    if model:
        # Allow per-call model override via env var (provider-swap friendly).
        old = os.environ.get("OPENAI_MODEL")
        os.environ["OPENAI_MODEL"] = model
        try:
            return str(call_llm(prompt).get("summary", "")).strip()
        finally:
            if old is None:
                os.environ.pop("OPENAI_MODEL", None)
            else:
                os.environ["OPENAI_MODEL"] = old

    parsed = call_llm(prompt)
    return str(parsed.get("summary", "")).strip()

