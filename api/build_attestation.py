#!/usr/bin/env python3
"""
api/build_attestation.py

Builds a public, machine-readable "GodScore attestation" JSON from the
generated v1 output artifact.

Outputs a compact object suitable for publishing at:
  /.well-known/godscore.json

Usage:
  python api/build_attestation.py <input_output_json> <output_attestation_json>

Example:
  python api/build_attestation.py api/out/godscore.output.v1.json attestation/godscore.json
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("root must be an object")
    return data


def save_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_get(d: Any, keys: list[str], default: Any) -> Any:
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python api/build_attestation.py <input_output_json> <output_attestation_json>")
        return 1

    in_path = argv[1]
    out_path = argv[2]

    data = load_json(in_path)

    version = safe_get(data, ["version"], "1.0.0")
    generated_at = safe_get(data, ["generated_at"], iso_now())
    ctx_repo = safe_get(data, ["context", "repo"], "unknown")
    ctx_ref = safe_get(data, ["context", "ref"], "unknown")
    ctx_sha = safe_get(data, ["context", "sha"], "unknown")
    ctx_run_id = safe_get(data, ["context", "run_id"], "unknown")

    outputs = safe_get(data, ["outputs"], {})
    if not isinstance(outputs, dict):
        outputs = {}

    metrics = safe_get(outputs, ["metrics"], {})
    if not isinstance(metrics, dict):
        metrics = {}

    # Minimal public surface (stable)
    public_metrics = {
        "chi_status": metrics.get("chi_status", "unknown"),
        "chi_ratio": metrics.get("chi_ratio", 0.0),
        "chi_drift_count": metrics.get("chi_drift_count", 0),
        "chi_drift_policy_ids": metrics.get("chi_drift_policy_ids", []),
        # Tier exports (Step 19+) if present
        "chi_drift_by_tier": metrics.get("chi_drift_by_tier", {}),
        "chi_max_drift_tier": metrics.get("chi_max_drift_tier", 0),
        "chi_enforced_tiers": metrics.get("chi_enforced_tiers", []),
    }

    attestation: Dict[str, Any] = {
        "attestation_version": "v1",
        "producer": "godscore-ci",
        "generated_at": generated_at,
        "source": {
            "repo": ctx_repo,
            "ref": ctx_ref,
            "sha": ctx_sha,
            "run_id": ctx_run_id,
        },
        "result": {
            # keep these if present (helpful for external consumers)
            "score": outputs.get("score", 0),
            "grade": outputs.get("grade", "N/A"),
            "threshold": outputs.get("threshold", 0),
            "pass": outputs.get("pass", True),
        },
        "metrics": public_metrics,
        "links": {
            # relative links, so they work anywhere Pages is hosted
            "dashboard": "/",
            "attestation": "/.well-known/godscore.json",
        },
    }

    save_json(out_path, attestation)
    print(f"✅ wrote attestation: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
