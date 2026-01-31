#!/usr/bin/env python3
"""
api/validate_v1.py

Zero-dependency validator for the godscore-ci API v1 contract.
Validates that a JSON payload OR schema:
- is valid JSON
- contains required keys
- has correct top-level types
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List


def err(msg: str) -> None:
    print(f"[invalid] {msg}")


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_iso8601_or_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if value == "ISO-8601":
        return True
    if "T" not in value:
        return False
    return value.endswith("Z") or ("+" in value[-6:] or "-" in value[-6:])


def require_keys(obj: Any, keys: List[str], where: str) -> bool:
    if not isinstance(obj, dict):
        err(f"{where} must be an object")
        return False
    missing = [k for k in keys if k not in obj]
    if missing:
        err(f"{where} missing keys: {', '.join(missing)}")
        return False
    return True


def require_type(value: Any, t: type | tuple[type, ...], where: str) -> bool:
    if not isinstance(value, t):
        err(f"{where} expected {t}, got {type(value)}")
        return False
    return True


def validate(payload: Dict[str, Any]) -> bool:
    required_top = [
        "version",
        "generated_at",
        "subject",
        "context",
        "inputs",
        "outputs",
    ]

    if not require_keys(payload, required_top, "root"):
        return False

    if not require_type(payload["version"], str, "version"):
        return False

    if not is_iso8601_or_placeholder(payload["generated_at"]):
        err("generated_at must be ISO-8601 or 'ISO-8601'")
        return False

    if not require_keys(payload["subject"], ["type", "id"], "subject"):
        return False

    if not require_keys(payload["context"], ["repo", "ref", "sha", "run_id"], "context"):
        return False

    if not require_keys(payload["inputs"], ["signals"], "inputs"):
        return False
    if not require_type(payload["inputs"]["signals"], list, "inputs.signals"):
        return False

    if not require_keys(
        payload["outputs"],
        ["score", "grade", "threshold", "pass", "explanations", "evidence", "metrics"],
        "outputs",
    ):
        return False

    return True


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print("Usage: python validate_v1.py <contract.json> <payload.json>")
        return 1

    try:
        _ = load_json(argv[1])
        ok(f"Loaded contract: {argv[1]}")
    except Exception as e:
        err(f"Contract load failed: {e}")
        return 1

    try:
        payload = load_json(argv[2])
        ok(f"Loaded payload: {argv[2]}")
    except Exception as e:
        err(f"Payload load failed: {e}")
        return 1

    if not isinstance(payload, dict):
        err("Payload root must be an object")
        return 1

    if validate(payload):
        ok("Payload matches v1 contract shape ✅")
        return 0

    err("Payload does NOT match v1 contract shape ❌")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
