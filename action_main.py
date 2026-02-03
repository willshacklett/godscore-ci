# godscore_ci/action_main.py
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from typing import Optional

from godscore_ci.scoring_pipeline import compute_score_pipeline


def _get_input(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    GitHub Actions passes inputs as env vars like INPUT_SCORE, INPUT_THRESHOLD, etc.
    """
    key = f"INPUT_{name.upper()}"
    return os.getenv(key, default)


def _normalize_01(value: str, default: float) -> float:
    try:
        x = float(value)
    except Exception:
        return default
    if x > 1.0:
        x = x / 100.0
    return max(0.0, min(1.0, x))


def _write_github_output(key: str, value: str) -> None:
    out_path = os.getenv("GITHUB_OUTPUT")
    if not out_path:
        # fallback
        print(f"::set-output name={key}::{value}")
        return
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")


def main() -> int:
    raw_score = _get_input("score")
    raw_threshold = _get_input("threshold", _get_input("min_score", "0.80") or "0.80")
    raw_enforce = _get_input("enforce", "false") or "false"
    raw_mode = _get_input("mode", "free") or "free"

    threshold = _normalize_01(raw_threshold, default=0.80)
    enforce = str(raw_enforce).strip().lower() in ("1", "true", "yes", "y", "on")
    mode = str(raw_mode).strip().lower()

    # Compute score: manual or AutoScore v1 -> GV -> GodScore
    res = compute_score_pipeline(raw_score=raw_score)

    score = res.godscore  # normalized 0..1
    gv = res.gv

    passed = score >= threshold
    effective_mode = "pro" if (mode == "pro" or mode == "paid") else "free"

    # --- Logs (human-readable, “stupid-simple”) ---
    print("=== GodScore CI ===")
    print(f"score_source: {res.source}")
    print(f"godscore: {score:.2f}  (0..1)")
    print(f"gv: {gv:.2f}        (0..1; lower is better)")
    print(f"threshold: {threshold:.2f}")
    print(f"mode: {effective_mode}")
    print(f"enforce: {enforce}")
    print("")
    print("=== Notes ===")
    for n in res.notes:
        print(f"- {n}")
    print("")
    print("=== GV Breakdown ===")
    for line in res.gv_explanation:
        print(line)

    # --- Outputs (for workflows / other steps) ---
    _write_github_output("godscore", f"{score:.4f}")
    _write_github_output("gv", f"{gv:.4f}")
    _write_github_output("passed", "true" if passed else "false")
    _write_github_output("effective_mode", effective_mode)
    _write_github_output("score_source", res.source)

    # Optional: write a small JSON blob for dashboards/archives
    payload = {
        "godscore": score,
        "gv": gv,
        "threshold": threshold,
        "passed": passed,
        "effective_mode": effective_mode,
        "score_source": res.source,
        "penalties": res.penalties,
        "signals": res.signals,
        "notes": res.notes,
        "gv_explanation": res.gv_explanation,
    }

    # If your dashboard pipeline wants a file, you now have a stable artifact path
    artifact_path = os.getenv("GODSCORE_OUTPUT_JSON", "").strip()
    if artifact_path:
        try:
            with open(artifact_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            print(f"\nWrote JSON output: {artifact_path}")
        except Exception as e:
            print(f"\nWarning: Failed to write JSON output ({artifact_path}): {e}")

    # --- Enforcement ---
    if enforce and not passed and effective_mode == "pro":
        print("\n❌ ENFORCEMENT: GodScore below threshold. Failing the build.")
        return 1

    if not passed:
        print("\n⚠️ GodScore below threshold (informational).")
    else:
        print("\n✅ GodScore meets threshold.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
