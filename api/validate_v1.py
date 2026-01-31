#!/usr/bin/env python3
"""
api/validate_v1.py

GodScore API v1 contract validator.

Validates the minimal, universal output surface.
Allows forward-compatible extensions.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fail(msg: str) -> None:
    print("❌ API Contract (v1) validation failed:")
    print(msg)
    sys.exit(1)


def require(obj: Dict[str, Any], key: str, typ) -> None:
    if key not in obj:
        fail(f"Missing required key: {key}")
    if not isinstance(obj[key], typ):
        fail(f"Key '{key}' must be {typ}")


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python api/validate_v1.py <schema.json> <output.json>")
        sys.exit(1)

    _, schema_path, output_path = sys.argv

    # Ensure schema exists (not shape-enforced)
    load_json(schema_path)
    data = load_json(output_path)

    # --- Required surface ---
    require(data, "outputs", dict)

    outputs = data["outputs"]
    require(outputs, "score", (int, float))
    require(outputs, "pass", bool)
    require(outputs, "metrics", dict)

    metrics = outputs["metrics"]

    # --- Minimal required metrics ---
    required_metrics = {
        "signal_count": int,
        "chi_drift_count": int,
        "chi_ratio": (int, float),
        "chi_status": str,
        "chi_drift_policy_ids": list,
    }

    for key, typ in required_metrics.items():
        if key not in metrics:
            fail(f"Missing required metrics.{key}")
        if not isinstance(metrics[key], typ):
            fail(f"metrics.{key} must be {typ}")

    # --- Optional metrics (allowed if present) ---
    optional_metrics = {
        "chi_policy_count": int,
        "chi_drift_by_tier": dict,
        "chi_max_drift_tier": int,
        "chi_enforced_tiers": list,
    }

    for key, typ in optional_metrics.items():
        if key in metrics and not isinstance(metrics[key], typ):
            fail(f"metrics.{key} must be {typ} if present")

    print("✅ API Contract (v1) validation passed")


if __name__ == "__main__":
    main()
