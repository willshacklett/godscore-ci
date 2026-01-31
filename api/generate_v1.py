#!/usr/bin/env python3
"""
api/generate_v1.py

Step 19:
- Export tier-aware CHI signals for external systems
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_policies(path: str) -> Dict[str, Dict[str, Any]]:
    try:
        data = load_json(path)
    except Exception:
        return {}
    out = {}
    for p in data.get("policies", []):
        pid = p.get("id")
        if isinstance(pid, str):
            out[pid] = p
    return out


def policy_tier(p: Dict[str, Any]) -> int:
    try:
        return int(p.get("tier", 0))
    except Exception:
        return 0


def main() -> None:
    template = load_json("api/example_output.v1.json")
    policy_path = os.getenv("GODSCORE_POLICY_PATH", "api/policy.v1.json")
    policies = load_policies(policy_path)

    template["generated_at"] = iso_now()
    metrics = template["outputs"]["metrics"]

    drift_ids = metrics.get("chi_drift_policy_ids", [])
    drift_by_tier: Dict[str, List[str]] = {}
    enforced_tiers = set()
    max_tier = 0

    for pid in drift_ids:
        p = policies.get(pid)
        tier = policy_tier(p) if p else 0
        drift_by_tier.setdefault(str(tier), []).append(pid)
        max_tier = max(max_tier, tier)

    for p in policies.values():
        enforced_tiers.add(policy_tier(p))

    metrics["chi_drift_by_tier"] = drift_by_tier
    metrics["chi_max_drift_tier"] = max_tier
    metrics["chi_enforced_tiers"] = sorted(enforced_tiers)

    save_json("api/out/godscore.output.v1.json", template)


if __name__ == "__main__":
    main()
