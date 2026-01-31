#!/usr/bin/env python3
"""
api/validate_v1.py

Zero-dependency validator for the godscore-ci API v1 contract.
It validates that a JSON payload:
- is valid JSON
- contains required top-level keys
- has the expected basic types for core fields
- contains the required nested structures

Usage:
  python api/validate_v1.py api/schema.v1.json api/example_output.v1.json
Exit code:
  0 = valid
  1 = invalid
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Tuple


def err(msg: str) -> None:
    print(f"[invalid] {msg}")


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_iso8601-ish(value: Any) -> bool:
    # Minimal check: string with a 'T' and either 'Z' or timezone offset.
    if not isinstance(value, str):
        return False
    if "T" not in value:
        return False
    return value.endswith("Z") or ("+" in value[-6:] or "-" in value[-6:])


def require_keys(obj: Any, keys: List[str], where: str) -> List[str]:
    missing = []
    if not isinstance(obj, dict):
        return keys[:]  # everything "missing" if not a dict
    for k in keys:
        if k not in obj:
            missing.append(k)
    if missing:
        err(f"{where} missing keys: {', '.join(missing)}")
    return missing


def require_type(value: Any, t: type, where: str) -> bool:
    if not isinstance(value, t):
        err(f"{where} expected {t.__name__}, got {type(value).__name__}")
        return False
    return True


def validate_payload(payload: Dict[str, Any]) -> bool:
    valid = True

    # Required top-level keys
    top_required = [
        "version",
        "generated_at",
        "subject",
        "context",
        "inputs",
        "outputs",
    ]
    if require_keys(payload, top_required, "root"):
        return False

    # version
    valid &= require_type(payload.get("version"), str, "root.version")

    # generated_at
    ga = payload.get("generated_at")
    if not require_type(ga, str, "root.generated_at"):
        valid = False
    else:
        # don't be strict yet, just sanity-check
        if not is_iso8601-ish(ga):
            err("root.generated_at should look like ISO-8601 (e.g., 2026-01-31T12:34:56Z)")
            valid = False

    # subject
    subject = payload.get("subject")
    if not require_type(subject, dict, "root.subject"):
        return False
    if require_keys(subject, ["type", "id"], "subject"):
        return False
    valid &= require_type(subject.get("type"), str, "subject.type")
    valid &= require_type(subject.get("id"), str, "subject.id")

    # context
    context = payload.get("context")
    if not require_type(context, dict, "root.context"):
        return False
    ctx_required = ["repo", "ref", "sha", "run_id"]
    if require_keys(context, ctx_required, "context"):
        return False
    for k in ctx_required:
        valid &= require_type(context.get(k), str, f"context.{k}")

    # inputs
    inputs = payload.get("inputs")
    if not require_type(inputs, dict, "root.inputs"):
        return False
    if require_keys(inputs, ["signals"], "inputs"):
        return False
    valid &= require_type(inputs.get("signals"), list, "inputs.signals")

    # outputs
    outputs = payload.get("outputs")
    if not require_type(outputs, dict, "root.outputs"):
        return False

    out_required = [
        "score",
        "grade",
        "threshold",
        "pass",
        "explanations",
        "evidence",
        "metrics",
    ]
    if require_keys(outputs, out_required, "outputs"):
        return False

    valid &= require_type(outputs.get("score"), (int, float), "outputs.score")
    valid &= require_type(outputs.get("grade"), str, "outputs.grade")
    valid &= require_type(outputs.get("threshold"), (int, float), "outputs.threshold")
    valid &= require_type(outputs.get("pass"), bool, "outputs.pass")
    valid &= require_type(outputs.get("explanations"), list, "outputs.explanations")
    valid &= require_type(outputs.get("evidence"), list, "outputs.evidence")
    valid &= require_type(outputs.get("metrics"), dict, "outputs.metrics")

    return bool(valid)


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print("Usage: python api/validate_v1.py <contract.json> <payload.json>")
        return 1

    contract_path, payload_path = argv[1], argv[2]

    # We load the contract file mostly to ensure it exists / is valid JSON.
    try:
        _ = load_json(contract_path)
        ok(f"Loaded contract: {contract_path}")
    except Exception as e:
        err(f"Failed to load contract JSON: {e}")
        return 1

    try:
        payload = load_json(payload_path)
        ok(f"Loaded payload: {payload_path}")
    except Exception as e:
        err(f"Failed to load payload JSON: {e}")
        return 1

    if not isinstance(payload, dict):
        err("payload root must be a JSON object")
        return 1

    if validate_payload(payload):
        ok("Payload matches v1 contract shape ✅")
        return 0

    err("Payload does NOT match v1 contract shape ❌")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
