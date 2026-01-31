#!/usr/bin/env python3
"""
api/generate_v1.py

Minimal generator for godscore-ci API v1 output.
- Reads a base template JSON (schema/example)
- Injects context from env vars (GitHub Actions-friendly)
- Optionally reads signals from a JSON file (GODSCORE_SIGNALS_PATH)
- Emits baseline machine-readable explanations (outputs.explanations[])
- Writes a fully-formed v1 output JSON

Usage:
  python api/generate_v1.py api/example_output.v1.json api/out/godscore.output.v1.json
Optional:
  export GODSCORE_SIGNALS_PATH=api/example_signals.v1.json
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


def load_signals(path: str) -> list[dict[str, Any]]:
    """
    Loads signals from a JSON file shaped like:
      { "version": "1.0.0", "signals": [ ... ] }

    Returns [] if missing or invalid (generator stays resilient).
    """
    if not path:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("signals"), list):
            out: list[dict[str, Any]] = []
            for s in data["signals"]:
                if isinstance(s, dict):
                    out.append(s)
            return out
    except FileNotFoundError:
        return []
    except Exception:
        return []
    return []


def baseline_explanations(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Machine-readable explanations. No vibes, no prose walls.
    Keep IDs stable so downstream tooling can rely on them.
    """
    signal_ids: list[str] = []
    for s in signals:
        sid = s.get("id")
        if isinstance(sid, str) and sid:
            signal_ids.append(sid)

    explanations: list[dict[str, Any]] = []

    explanations.append(
        {
            "id": "explain.api.contract.v1",
            "kind": "system",
            "severity": "info",
            "message": "API v1 contract output generated.",
            "details": {"contract_version": "1.0.0"},
            "signals": []
        }
    )

    explanations.append(
        {
            "id": "explain.inputs.signals.ingested",
            "kind": "system",
            "severity": "info",
            "message": "Signals ingested into inputs.signals.",
            "details": {"signal_count": len(signals)},
            "signals": signal_ids
        }
    )

    explanations.append(
        {
            "id": "explain.score.placeholder",
            "kind": "system",
            "severity": "info",
            "message": "Score is placeholder (0). Scoring logic not enabled yet.",
            "details": {"score": 0, "status": "placeholder"},
            "signals": []
        }
    )

    explanations.append(
        {
            "id": "explain.enforcement.disabled",
            "kind": "enforcement",
            "severity": "info",
            "message": "Enforcement is not applied by this generator.",
            "details": {"enforcement": "disabled"},
            "signals": []
        }
    )

    return explanations


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

    signals_path = env("GODSCORE_SIGNALS_PATH", "")
    signals = load_signals(signals_path) if signals_path else []

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

    # Inputs: signals
    data.setdefault("inputs", {})
    data["inputs"]["signals"] = signals

    # Outputs: baseline explanations (stable structure)
    data.setdefault("outputs", {})
    data["outputs"].setdefault("explanations", [])
    data["outputs"]["explanations"] = baseline_explanations(signals)

    save_json(output_path, data)
    print(f"[ok] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
