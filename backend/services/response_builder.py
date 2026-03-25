"""Helpers for building consistent API responses."""

from __future__ import annotations

from typing import Any, Dict


def build_success_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "success", "data": payload}


def build_error_response(message: str) -> Dict[str, Any]:
    return {"status": "error", "message": message}

