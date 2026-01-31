#!/usr/bin/env python3
"""
api/chi_gate.py

Optional CHI enforcement gate.
- Reads API v1 output JSON (default: api/out/godscore.output.v1.json)
- If GODSCORE_CHI_ENFORCE=true and CHI status is drifting => exit 1
- Otherwise exit 0

Usage:
  python api/chi_gate.py api/out/godscore.output.v1.json
Env:
  GODSCORE_CHI_ENFORCE=true|false   (default false)
  GODSCORE_CHI_ALLOW_UNKNOWN=true|false (default true)
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("root must be an object")
    return data


def env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip().lower()
    return v in ("1", "true", "yes", "y", "on")


def safe_get(d: Any, keys: list[str], default: Any) -> Any:
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python api/chi_gate.py <output.json>")
        return 1

    path = argv[1]
    enforce = env_bool("GODSCORE_CHI_ENFORCE", False)
    allow_unknown = env_bool("GODSCORE_CHI_ALLOW_UNKNOWN", True)

    data = load_json(path)
    repo = safe_get(data, ["context", "repo"], "unknown")
    sha = safe_get(data, ["context", "sha"], "unknown")

    metrics = safe_get(data, ["outputs", "metrics"], {})
    if not isinstance(metrics, dict):
        metrics = {}

    chi_status = metrics.get("chi_status", "unknown")
    chi_ratio = metrics.get("chi_ratio", 0.0)
    chi_drift = metrics.get("chi_drift_count", 0)

    # Always print what we saw (helpful even when not enforcing)
    print("[chi-gate] repo:", repo)
    print("[chi-gate] sha:", sha)
    print("[chi-gate] enforce:", enforce)
    print("[chi-gate] status:", chi_status)
    print("[chi-gate] ratio:", chi_ratio)
    print("[chi-gate] drift_count:", chi_drift)

    if not enforce:
        print("[chi-gate] enforcement disabled -> PASS")
        return 0

    if chi_status == "unknown" and allow_unknown:
        print("[chi-gate] status unknown and allow_unknown=true -> PASS")
        return 0

    if chi_status == "drifting":
        print("[chi-gate] CHI drifting -> FAIL")
        return 1

    print("[chi-gate] CHI not drifting -> PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
