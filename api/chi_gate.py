#!/usr/bin/env python3
"""
api/chi_gate.py

Tier-aware optional CHI enforcement gate.

Reads:
- API v1 output JSON (generated artifact)
- Policy file (default: api/policy.v1.json)

Behavior:
- If GODSCORE_CHI_ENFORCE=false -> PASS
- If enforce=true:
    - If chi_status == drifting:
        - Fail ONLY if any drifted policy has tier >= GODSCORE_CHI_MIN_TIER
    - Otherwise PASS

Usage:
  python api/chi_gate.py api/out/godscore.output.v1.json

Env:
  GODSCORE_CHI_ENFORCE=true|false        (default false)
  GODSCORE_CHI_ALLOW_UNKNOWN=true|false  (default true)
  GODSCORE_POLICY_PATH=path              (default api/policy.v1.json)
  GODSCORE_CHI_MIN_TIER=int              (default 2)
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional


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


def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v.strip())
    except Exception:
        return default


def safe_get(d: Any, keys: List[str], default: Any) -> Any:
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def load_policy_index(path: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns {policy_id: policy_obj}
    Accepts:
      { "policies": [ { "id": "...", "tier": 0..3, ... } ] }
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


def policy_tier(policy_obj: Optional[Dict[str, Any]]) -> int:
    if not isinstance(policy_obj, dict):
        return 0
    t = policy_obj.get("tier", 0)
    if isinstance(t, bool):
        return 0
    if isinstance(t, int):
        return t
    try:
        return int(t)
    except Exception:
        return 0


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python api/chi_gate.py <output.json>")
        return 1

    out_path = argv[1]

    enforce = env_bool("GODSCORE_CHI_ENFORCE", False)
    allow_unknown = env_bool("GODSCORE_CHI_ALLOW_UNKNOWN", True)
    policy_path = os.getenv("GODSCORE_POLICY_PATH", "api/policy.v1.json")
    min_tier = env_int("GODSCORE_CHI_MIN_TIER", 2)

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

    print("[chi-gate] repo:", repo)
    print("[chi-gate] sha:", sha)
    print("[chi-gate] enforce:", enforce)
    print("[chi-gate] policy_path:", policy_path)
    print("[chi-gate] min_tier:", min_tier)
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

    # CHI drifting: enforce only for drifted policies at/above min tier
    pol_idx = load_policy_index(policy_path)

    hits: List[str] = []
    unknown: List[str] = []

    for pid in drift_ids:
        if not isinstance(pid, str) or not pid:
            continue
        pobj = pol_idx.get(pid)
        if pobj is None:
            unknown.append(pid)
            continue
        t = policy_tier(pobj)
        if t >= min_tier:
            hits.append(pid)

    if hits:
        print("[chi-gate] FAIL: drift includes policies at/above min tier:")
        for pid in hits:
            t = policy_tier(pol_idx.get(pid))
            print(f" - {pid} (tier {t})")
        return 1

    print("[chi-gate] PASS: drifting only below min tier")
    if unknown:
        print("[chi-gate] note: drifted policies not found in policy file (treated as tier 0):")
        for pid in unknown:
            print(" -", pid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
