#!/usr/bin/env python3
"""
api/validate_v1.py

Zero-dependency validator for the godscore-ci API v1 contract.
Validates that a JSON payload OR schema:
- is valid JSON
- contains required keys
- has correct top-level types
- explanations[] and evidence[] are structured objects
- recommendations[] (optional) is structured if present
- todos[] (optional) is structured if present
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

    # explanations must be a list of objects with required keys
    exps = payload["outputs"]["explanations"]
    if not require_type(exps, list, "outputs.explanations"):
        return False

    for i, ex in enumerate(exps):
        if not isinstance(ex, dict):
            err(f"outputs.explanations[{i}] must be an object")
            return False
        for k in ["id", "kind", "severity", "message", "details", "signals"]:
            if k not in ex:
                err(f"outputs.explanations[{i}] missing key: {k}")
                return False
        if not isinstance(ex["id"], str) or not ex["id"]:
            err(f"outputs.explanations[{i}].id must be a non-empty string")
            return False
        if not isinstance(ex["kind"], str) or not ex["kind"]:
            err(f"outputs.explanations[{i}].kind must be a non-empty string")
            return False
        if not isinstance(ex["severity"], str) or not ex["severity"]:
            err(f"outputs.explanations[{i}].severity must be a non-empty string")
            return False
        if not isinstance(ex["message"], str) or not ex["message"]:
            err(f"outputs.explanations[{i}].message must be a non-empty string")
            return False
        if not isinstance(ex["details"], dict):
            err(f"outputs.explanations[{i}].details must be an object")
            return False
        if not isinstance(ex["signals"], list):
            err(f"outputs.explanations[{i}].signals must be a list")
            return False

    # evidence must be a list of objects with required keys
    evs = payload["outputs"]["evidence"]
    if not require_type(evs, list, "outputs.evidence"):
        return False

    for i, ev in enumerate(evs):
        if not isinstance(ev, dict):
            err(f"outputs.evidence[{i}] must be an object")
            return False
        for k in ["id", "kind", "source", "locator", "summary", "details", "signals"]:
            if k not in ev:
                err(f"outputs.evidence[{i}] missing key: {k}")
                return False
        if not isinstance(ev["id"], str) or not ev["id"]:
            err(f"outputs.evidence[{i}].id must be a non-empty string")
            return False
        if not isinstance(ev["kind"], str) or not ev["kind"]:
            err(f"outputs.evidence[{i}].kind must be a non-empty string")
            return False
        if not isinstance(ev["source"], str) or not ev["source"]:
            err(f"outputs.evidence[{i}].source must be a non-empty string")
            return False
        if not isinstance(ev["locator"], str) or not ev["locator"]:
            err(f"outputs.evidence[{i}].locator must be a non-empty string")
            return False
        if not isinstance(ev["summary"], str) or not ev["summary"]:
            err(f"outputs.evidence[{i}].summary must be a non-empty string")
            return False
        if not isinstance(ev["details"], dict):
            err(f"outputs.evidence[{i}].details must be an object")
            return False
        if not isinstance(ev["signals"], list):
            err(f"outputs.evidence[{i}].signals must be a list")
            return False

    # metrics must be an object
    if not require_type(payload["outputs"]["metrics"], dict, "outputs.metrics"):
        return False

    # recommendations[] is OPTIONAL, but if present must be valid
    if "recommendations" in payload["outputs"]:
        recs = payload["outputs"]["recommendations"]
        if not require_type(recs, list, "outputs.recommendations"):
            return False

        for i, rec in enumerate(recs):
            if not isinstance(rec, dict):
                err(f"outputs.recommendations[{i}] must be an object")
                return False
            for k in ["id", "kind", "severity", "message", "details", "policies", "evidence"]:
                if k not in rec:
                    err(f"outputs.recommendations[{i}] missing key: {k}")
                    return False
            if not isinstance(rec["id"], str) or not rec["id"]:
                err(f"outputs.recommendations[{i}].id must be a non-empty string")
                return False
            if not isinstance(rec["kind"], str) or not rec["kind"]:
                err(f"outputs.recommendations[{i}].kind must be a non-empty string")
                return False
            if not isinstance(rec["severity"], str) or not rec["severity"]:
                err(f"outputs.recommendations[{i}].severity must be a non-empty string")
                return False
            if not isinstance(rec["message"], str) or not rec["message"]:
                err(f"outputs.recommendations[{i}].message must be a non-empty string")
                return False
            if not isinstance(rec["details"], dict):
                err(f"outputs.recommendations[{i}].details must be an object")
                return False
            if not isinstance(rec["policies"], list):
                err(f"outputs.recommendations[{i}].policies must be a list")
                return False
            if not isinstance(rec["evidence"], list):
                err(f"outputs.recommendations[{i}].evidence must be a list")
                return False

    # todos[] is OPTIONAL, but if present must be valid
    if "todos" in payload["outputs"]:
        todos = payload["outputs"]["todos"]
        if not require_type(todos, list, "outputs.todos"):
            return False

        for i, td in enumerate(todos):
            if not isinstance(td, dict):
                err(f"outputs.todos[{i}] must be an object")
                return False
            for k in ["id", "title", "priority", "status", "actions", "policy", "evidence_kind", "evidence_locator"]:
                if k not in td:
                    err(f"outputs.todos[{i}] missing key: {k}")
                    return False
            if not isinstance(td["id"], str) or not td["id"]:
                err(f"outputs.todos[{i}].id must be a non-empty string")
                return False
            if not isinstance(td["title"], str) or not td["title"]:
                err(f"outputs.todos[{i}].title must be a non-empty string")
                return False
            if not isinstance(td["priority"], str) or not td["priority"]:
                err(f"outputs.todos[{i}].priority must be a non-empty string")
                return False
            if not isinstance(td["status"], str) or not td["status"]:
                err(f"outputs.todos[{i}].status must be a non-empty string")
                return False
            if not isinstance(td["actions"], list):
                err(f"outputs.todos[{i}].actions must be a list")
                return False
            for j, act in enumerate(td["actions"]):
                if not isinstance(act, dict):
                    err(f"outputs.todos[{i}].actions[{j}] must be an object")
                    return False
                for ak in ["type", "target", "payload"]:
                    if ak not in act:
                        err(f"outputs.todos[{i}].actions[{j}] missing key: {ak}")
                        return False
                if not isinstance(act["type"], str) or not act["type"]:
                    err(f"outputs.todos[{i}].actions[{j}].type must be a non-empty string")
                    return False
                if not isinstance(act["target"], str) or not act["target"]:
                    err(f"outputs.todos[{i}].actions[{j}].target must be a non-empty string")
                    return False
                if not isinstance(act["payload"], dict):
                    err(f"outputs.todos[{i}].actions[{j}].payload must be an object")
                    return False
            if not isinstance(td["policy"], str) or not td["policy"]:
                err(f"outputs.todos[{i}].policy must be a non-empty string")
                return False
            if not isinstance(td["evidence_kind"], str) or not td["evidence_kind"]:
                err(f"outputs.todos[{i}].evidence_kind must be a non-empty string")
                return False
            if not isinstance(td["evidence_locator"], str) or not td["evidence_locator"]:
                err(f"outputs.todos[{i}].evidence_locator must be a non-empty string")
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
