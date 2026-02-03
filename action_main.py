# godscore_ci/action_main.py
from __future__ import annotations

import json
import os
import sys
from typing import Optional

from godscore_ci.scoring_pipeline import compute_score_pipeline


def _get_input(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(f"INPUT_{name.upper()}", default)


def _normalize_01(value: str, default: float) -> float:
    try:
        x = float(value)
    except Exception:
        return default
    if x > 1.0:
        x = x / 100.0
    return max(0.0, min(1.0, x))


def _write_output(key: str, value: str) -> None:
    path = os.getenv("GITHUB_OUTPUT")
    if not path:
        print(f"::set-output name={key}::{value}")
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")


def main() -> int:
    # ---- Inputs ----
    raw_score = _get_input("score")
    raw_threshold = _get_input("threshold", _get_input("min_score", "0.80") or "0.80")
    raw_mode = _get_input("mode", "free") or "free"
    raw_enforce = _get_input("enforce", "false") or "false"

    threshold = _normalize_01(raw_threshold, 0.80)
    mode = raw_mode.strip().lower()
    enforce = raw_enforce.strip().lower() in ("1", "true", "yes", "y", "on")

    # ---- Compute score ----
    res = compute_score_pipeline(raw_score=raw_score)

    godscore = res.godscore
    gv = res.gv
    passed = godscore >= threshold
    effective_mode = "pro" if mode == "pro" else "free"

    # ---- Logs ----
    print("=== GodScore CI ===")
    print(f"score_source: {res.source}")
    print(f"godscore: {godscore:.2f} (0..1)")
    print(f"gv: {gv:.2f} (0..1, lower is better)")
    print(f"threshold: {threshold:.2f}")
    print(f"mode: {effective_mode}")
    print(f"enforce: {enforce}")
    print("")
    print("=== Notes ===")
    for note in res.notes:
        print(f"- {note}")
    print("")
    print("=== GV Breakdown ===")
    for line in res.gv_explanation:
        print(line)

    # ---- Outputs ----
    _write_output("godscore", f"{godscore:.4f}")
    _write_output("gv", f"{gv:.4f}")
    _write_output("passed", "true" if passed else "false")
    _write_output("effective_mode", effective_mode)
    _write_output("score_source", res.source)

    # ---- JSON Artifact (ALWAYS WRITTEN) ----
    payload = {
        "godscore": godscore,
        "gv": gv,
        "passed": passed,
        "threshold": threshold,
        "mode": effective_mode,
        "score_source": res.source,
        "penalties": res.penalties,
        "signals": res.signals,
        "notes": res.notes,
        "gv_explanation": res.gv_explanation,
    }

    artifact_path = "godscore.json"
    try:
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"\nWrote GodScore JSON artifact: {artifact_path}")
    except Exception as e:
        print(f"\nWARNING: Failed to write GodScore JSON artifact: {e}")

    # ---- Enforcement ----
    if enforce and effective_mode == "pro" and not passed:
        print("\n❌ ENFORCEMENT: GodScore below threshold. Failing build.")
        return 1

    if passed:
        print("\n✅ GodScore meets threshold.")
    else:
        print("\n⚠️ GodScore below threshold (informational).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
