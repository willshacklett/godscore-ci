#!/usr/bin/env python3
"""
api/chi_gate.py

Policy-aware optional CHI enforcement gate.

Reads:
- API v1 output JSON (generated artifact)
- Policy file (default: api/policy.v1.json)

Behavior:
- If GODSCORE_CHI_ENFORCE=false -> PASS
- If enforce=true:
    - If chi_status == drifting:
        - Fail ONLY if any drifted policy is marked must_enforce=true
    - Otherwise PASS

Usage:
  python api/chi_gate.py api/out/godscore.output.v1.json

Env:
  GODSCORE_CHI_ENFORCE=true|false        (default false)
  GODSCORE_CHI_ALLOW_UNKNOWN=true|false  (default true)
  GODSCORE_POLICY_PATH=path              (default api/policy.v1.json)
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List


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


def safe_get(d: Any, keys: List[str], default: Any) -> Any:
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def load_policies(path: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns a dict index {policy_id: policy_obj}
    Accepts:
      { "policies": [ { "id": "...", "must_enforce": true/false, ... } ] }
    """
    try:
        data = load_json(path)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

    policies = data.get("policies", [])
    if not isinstance(policies, list):
        return {}

    idx: Dict[str, Dict[str, Any]] = {}
    for p in policies:
        if not isinstance(p, dict):
            continue
        pid = p.get("id")
        if isinstance(pid, str) and pid:
            idx[pid] = p
    return idx


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python api/chi_gate.py <output.json>")
        return 1

    out_path = argv[1]
    enforce = env_bool("GODSCORE_CHI_ENFORCE", False)
    allow_unknown = env_bool("GODSCORE_CHI_ALLOW_UNKNOWN", True)
    policy_path = os.getenv("GODSCORE_POLICY_PATH", "api/policy.v1.json")

    data = load_json(out_path)

    repo = safe_get(data, ["context", "repo"], "unknown")
    sha = safe_get(data, ["context", "sha"], "unknown")

    metrics = safe_get(data, ["outputs", "metrics"], {})
    if not isinstance(metrics, dict):
        metrics = {}

    chi_status = metrics.get("chi_status", "unknown")
    chi_ratio = metrics.get("chi_ratio", 0.0)
    drift_ids = metrics.get("chi_drift_policy_ids", [])
    if not isinstance(drift_ids, list):
        drift_ids = []

    # print what we saw (useful even when not enforcing)
    print("[chi-gate] repo:", repo)
    print("[chi-gate] sha:", sha)
    print("[chi-gate] enforce:", enforce)
    print("[chi-gate] policy_path:", policy_path)
    print("[chi-gate] status:", chi_status)
    print("[chi-gate] ratio:", chi_ratio)
    print("[chi-gate] drifted_policies:", drift_ids)

    if not enforce:
        print("[chi-gate] enforcement disabled -> PASS")
        return 0

    if chi_status == "unknown" and allow_unknown:
        print("[chi-gate] status unknown and allow_unknown=true -> PASS")
        return 0

    if chi_status != "drifting":
        print("[chi-gate] CHI not drifting -> PASS")
        return 0

    # CHI drifting: enforce only on must_enforce policies
    pol_idx = load_policies(policy_path)

    must_enforce_hits: List[str] = []
    unknown_policies: List[str] = []

    for pid in drift_ids:
        if not isinstance(pid, str) or not pid:
            continue
        p = pol_idx.get(pid)
        if p is None:
            unknown_policies.append(pid)
            continue
        me = p.get("must_enforce", False)
        if isinstance(me, bool) and me:
            must_enforce_hits.append(pid)

    if must_enforce_hits:
        print("[chi-gate] FAIL: drift includes must_enforce policies:")
        for pid in must_enforce_hits:
            print(" -", pid)
        return 1

    # If drifting but only non-must policies drifted, allow
    print("[chi-gate] PASS: drifting only on non-must policies")
    if unknown_policies:
        print("[chi-gate] note: drifted policies not found in policy file (treated as non-must):")
        for pid in unknown_policies:
            print(" -", pid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
