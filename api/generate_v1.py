#!/usr/bin/env python3
"""
api/generate_v1.py

GodScore API v1 generator.

Modes:
1) Full generation:
   generate_v1.py <input.json> <output.json>
   - guarantees minimal universal CHI metrics

2) Extend mode:
   generate_v1.py
   - extends existing output in-place
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict


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
    return {
        p["id"]: p
        for p in data.get("policies", [])
        if isinstance(p, dict) and "id" in p
    }


def policy_tier(p: Dict[str, Any]) -> int:
    try:
        return int(p.get("tier", 0))
    except Exception:
        return 0


def ensure_universal_chi(metrics: Dict[str, Any]) -> None:
    """Guarantee minimal universal CHI metrics."""
    metrics.setdefault("chi_drift_count", 0)
    metrics.setdefault("chi_ratio", 0.0)
    metrics.setdefault("chi_status", "unknown")
    metrics.setdefault("chi_drift_policy_ids", [])


def extend_with_tiers(data: Dict[str, Any]) -> None:
    policy_path = os.getenv("GODSCORE_POLICY_PATH", "api/policy.v1.json")
    policies = load_policies(policy_path)

    outputs = data.setdefault("outputs", {})
    metrics = outputs.setdefault("metrics", {})

    # 🔒 Guarantee contract surface
    ensure_universal_chi(metrics)

    drift_ids = metrics.get("chi_drift_policy_ids", [])

    drift_by_tier: Dict[str, list[str]] = {}
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


def main() -> None:
    # --- Mode 1: full generation (API Contract) ---
    if len(sys.argv) == 3:
        _, input_path, output_path = sys.argv
        data = load_json(input_path)
        data["generated_at"] = iso_now()
        extend_with_tiers(data)
        save_json(output_path, data)
        return

    # --- Mode 2: extend existing output ---
    output_path = "api/out/godscore.output.v1.json"
    data = load_json(output_path)
    extend_with_tiers(data)
    save_json(output_path, data)


if __name__ == "__main__":
    main()
