#!/usr/bin/env python3
"""
api/render_summary.py

Human-readable summary renderer for godscore-ci API v1 output.
Reads the generated output JSON and prints:
- CHI status + ratio
- Drifted policy IDs
- Top todos (titles + priorities)

Usage:
  python api/render_summary.py api/out/godscore.output.v1.json
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("root must be an object")
    return data


def safe_get(d: Any, path: List[str], default: Any) -> Any:
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python api/render_summary.py <output.json>")
        return 1

    out_path = argv[1]
    data = load_json(out_path)

    version = safe_get(data, ["version"], "unknown")
    generated_at = safe_get(data, ["generated_at"], "unknown")
    repo = safe_get(data, ["context", "repo"], "unknown")
    sha = safe_get(data, ["context", "sha"], "unknown")

    metrics = safe_get(data, ["outputs", "metrics"], {})
    if not isinstance(metrics, dict):
        metrics = {}

    chi_status = metrics.get("chi_status", "unknown")
    chi_ratio = metrics.get("chi_ratio", 0.0)
    chi_policy_count = metrics.get("chi_policy_count", 0)
    chi_enforced_count = metrics.get("chi_enforced_count", 0)
    chi_drift_count = metrics.get("chi_drift_count", 0)

    drift_ids = metrics.get("chi_drift_policy_ids", [])
    if not isinstance(drift_ids, list):
        drift_ids = []

    todos = safe_get(data, ["outputs", "todos"], [])
    if not isinstance(todos, list):
        todos = []

    # Header
    print("========================================")
    print("godscore-ci summary")
    print("========================================")
    print(f"version:      {version}")
    print(f"generated_at: {generated_at}")
    print(f"repo:         {repo}")
    print(f"sha:          {sha}")
    print("")

    # CHI block
    try:
        ratio_str = f"{float(chi_ratio):.3f}"
    except Exception:
        ratio_str = "0.000"

    print("CHI (Constraint Honesty Index)")
    print("----------------------------------------")
    print(f"status:       {chi_status}")
    print(f"ratio:        {ratio_str}")
    print(f"policies:     {chi_policy_count}")
    print(f"enforced:     {chi_enforced_count}")
    print(f"drift:        {chi_drift_count}")

    if len(drift_ids) > 0:
        print("")
        print("drifted policies:")
        for pid in drift_ids[:20]:
            print(f" - {pid}")
        if len(drift_ids) > 20:
            print(f" ... (+{len(drift_ids) - 20} more)")

    print("")

    # Todos block (top 10)
    print("Next actions (todos)")
    print("----------------------------------------")
    if len(todos) == 0:
        print(" - none")
    else:
        shown = 0
        for td in todos:
            if not isinstance(td, dict):
                continue
            title = td.get("title", "untitled")
            priority = td.get("priority", "low")
            status = td.get("status", "open")
            print(f" - [{status}] ({priority}) {title}")
            shown += 1
            if shown >= 10:
                break
        if len(todos) > 10:
            print(f" ... (+{len(todos) - 10} more)")

    print("")
    print("========================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
