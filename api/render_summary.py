#!/usr/bin/env python3
"""
api/render_summary.py

Human-readable summary renderer for godscore-ci API v1 output.
- Prints a clean console summary
- Writes a Markdown summary to $GITHUB_STEP_SUMMARY if available

Usage:
  python api/render_summary.py api/out/godscore.output.v1.json
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


def safe_get(d: Any, path: List[str], default: Any) -> Any:
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def fmt_ratio(val: Any) -> str:
    try:
        return f"{float(val):.3f}"
    except Exception:
        return "0.000"


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
    chi_ratio = fmt_ratio(metrics.get("chi_ratio", 0.0))
    chi_policy_count = metrics.get("chi_policy_count", 0)
    chi_enforced_count = metrics.get("chi_enforced_count", 0)
    chi_drift_count = metrics.get("chi_drift_count", 0)

    drift_ids = metrics.get("chi_drift_policy_ids", [])
    if not isinstance(drift_ids, list):
        drift_ids = []

    todos = safe_get(data, ["outputs", "todos"], [])
    if not isinstance(todos, list):
        todos = []

    # --------------------
    # Console output
    # --------------------
    print("========================================")
    print("godscore-ci summary")
    print("========================================")
    print(f"version:      {version}")
    print(f"generated_at: {generated_at}")
    print(f"repo:         {repo}")
    print(f"sha:          {sha}")
    print("")
    print("CHI (Constraint Honesty Index)")
    print("----------------------------------------")
    print(f"status:       {chi_status}")
    print(f"ratio:        {chi_ratio}")
    print(f"policies:     {chi_policy_count}")
    print(f"enforced:     {chi_enforced_count}")
    print(f"drift:        {chi_drift_count}")

    if drift_ids:
        print("")
        print("drifted policies:")
        for pid in drift_ids[:20]:
            print(f" - {pid}")

    print("")
    print("Next actions (todos)")
    print("----------------------------------------")
    if not todos:
        print(" - none")
    else:
        for td in todos[:10]:
            if not isinstance(td, dict):
                continue
            title = td.get("title", "untitled")
            priority = td.get("priority", "low")
            status = td.get("status", "open")
            print(f" - [{status}] ({priority}) {title}")

    print("")
    print("========================================")

    # --------------------
    # GitHub Step Summary (Markdown)
    # --------------------
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("## 🧭 GodScore CI Summary\n\n")
            f.write(f"**Repo:** `{repo}`  \n")
            f.write(f"**SHA:** `{sha}`  \n")
            f.write(f"**Generated:** `{generated_at}`  \n\n")

            f.write("### Constraint Honesty Index (CHI)\n\n")
            f.write("| Metric | Value |\n")
            f.write("|------|-------|\n")
            f.write(f"| Status | **{chi_status}** |\n")
            f.write(f"| Ratio | `{chi_ratio}` |\n")
            f.write(f"| Policies | `{chi_policy_count}` |\n")
            f.write(f"| Enforced | `{chi_enforced_count}` |\n")
            f.write(f"| Drift | `{chi_drift_count}` |\n\n")

            if drift_ids:
                f.write("### ⚠️ Drifted Policies\n\n")
                for pid in drift_ids[:20]:
                    f.write(f"- `{pid}`\n")
                f.write("\n")

            f.write("### ✅ Next Actions\n\n")
            if not todos:
                f.write("- No open todos 🎉\n")
            else:
                for td in todos[:10]:
                    if not isinstance(td, dict):
                        continue
                    title = td.get("title", "untitled")
                    priority = td.get("priority", "low")
                    status = td.get("status", "open")
                    f.write(f"- **[{status}] ({priority})** {title}\n")
            f.write("\n---\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
