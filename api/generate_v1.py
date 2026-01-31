#!/usr/bin/env python3
"""
api/generate_v1.py

Minimal generator for godscore-ci API v1 output.
- Reads a base template JSON (schema shape / example)
- Injects context from environment variables (GitHub Actions-friendly)
- Writes a fully-formed v1 output JSON

Usage:
  python api/generate_v1.py api/example_output.v1.json api/out/godscore.output.v1.json
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
        raise ValueError("template root must be a JSON object")
    return data


def save_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.write("\n")


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return v if (v is not None and v != "") else default


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python api/generate_v1.py <template.json> <output.json>")
        return 1

    template_path, output_path = argv[1], argv[2]
    data = load_json(template_path)

    repo = env("GITHUB_REPOSITORY", data.get("context", {}).get("repo", ""))
    ref = env("GITHUB_REF", data.get("context", {}).get("ref", ""))
    sha = env("GITHUB_SHA", data.get("context", {}).get("sha", ""))
    run_id = env("GITHUB_RUN_ID", data.get("context", {}).get("run_id", "local"))

    # Fill timestamps + context
    data["generated_at"] = iso_utc_now()
    data.setdefault("context", {})
    data["context"]["repo"] = repo
    data["context"]["ref"] = ref
    data["context"]["sha"] = sha
    data["context"]["run_id"] = run_id

    # Keep subject aligned with repo by default
    data.setdefault("subject", {})
    data["subject"]["type"] = data["subject"].get("type", "repo") or "repo"
    data["subject"]["id"] = repo or data["subject"].get("id", "unknown")

    save_json(output_path, data)
    print(f"[ok] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
