#!/usr/bin/env python3
"""
gv_gate.py
A simple CI gate for GodScore/Gv.

Behavior:
- mode=warn: never fails the build (exit 0), but prints warnings
- mode=fail: fails the build (exit 1) if score < threshold

Score scale handling:
- If score and threshold are both <= 1.0, treats them as 0..1
- Otherwise treats them as 0..100

Examples:
  python gv_gate.py --score 0.76 --threshold 0.80 --mode warn
  python gv_gate.py --score 76 --threshold 80 --mode fail
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass


DASHBOARD_URL = "https://willshacklett.github.io/godscore-ci/dashboard/"


@dataclass
class Normalized:
    score_100: float
    threshold_100: float
    scale: str  # "0..1" or "0..100"


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def normalize(score: float, threshold: float) -> Normalized:
    """
    Normalize score/threshold into 0..100 space for consistent messaging.
    """
    # Detect 0..1 usage
    if score <= 1.0 and threshold <= 1.0:
        s = _clamp(score, 0.0, 1.0) * 100.0
        t = _clamp(threshold, 0.0, 1.0) * 100.0
        return Normalized(score_100=s, threshold_100=t, scale="0..1")

    # Otherwise assume 0..100
    s = _clamp(score, 0.0, 100.0)
    t = _clamp(threshold, 0.0, 100.0)
    return Normalized(score_100=s, threshold_100=t, scale="0..100")


def verdict(score_100: float, threshold_100: float) -> tuple[bool, float]:
    """
    Returns (passed, margin). margin is score - threshold (in 0..100 space).
    """
    margin = score_100 - threshold_100
    return (margin >= 0.0), margin


def print_header():
    print("\n🛡️  GodScore CI Gate")
    print("──────────────────────────────")


def print_inputs(score: float, threshold: float, mode: str, norm: Normalized):
    print(f"Input score:      {score}")
    print(f"Input threshold:  {threshold}")
    print(f"Mode:             {mode}")
    print(f"Detected scale:   {norm.scale} (normalized to 0..100 for reporting)")
    print("")


def print_result(passed: bool, norm: Normalized, margin: float, mode: str):
    score_100 = norm.score_100
    thresh_100 = norm.threshold_100

    status = "PASS ✅" if passed else "FAIL ❌"
    print(f"Result:           {status}")
    print(f"GodScore:         {score_100:.1f} / 100")
    print(f"Threshold:        {thresh_100:.1f} / 100")
    if margin >= 0:
        print(f"Margin:           +{margin:.1f}")
    else:
        print(f"Margin:           {margin:.1f}")

    print("")
    if not passed:
        print("Why this matters:")
        print("  - GodScore is intended to reflect survivability / trust under change.")
        print("  - A low score means risk is rising faster than constraints are containing it.")
        print("")
        print("Fast recovery checklist:")
        print("  1) Fix failing tests (big score swings).")
        print("  2) Reduce lint findings (steady score climb).")
        print("  3) Tighten constraints / reduce instability sources.")
        print("")
        print(f"Live dashboard: {DASHBOARD_URL}")
        print("")

    # Mode-specific guidance
    if mode == "warn":
        if passed:
            print("Mode=warn: continuing (informational).")
        else:
            print("Mode=warn: continuing (informational — not failing the build).")
    else:
        if passed:
            print("Mode=fail: threshold satisfied. Continuing.")
        else:
            print("Mode=fail: enforcement triggered. Failing the build.")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="GodScore/Gv CI gate")
    p.add_argument("--score", required=True, help="Score to evaluate (0..1 or 0..100).")
    p.add_argument("--threshold", required=True, help="Minimum allowed score (0..1 or 0..100).")
    p.add_argument(
        "--mode",
        required=False,
        default="warn",
        choices=["warn", "fail"],
        help="warn = never fail build, fail = enforce threshold",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        score = float(args.score)
    except ValueError:
        print(f"ERROR: --score must be a number, got: {args.score!r}")
        return 2

    try:
        threshold = float(args.threshold)
    except ValueError:
        print(f"ERROR: --threshold must be a number, got: {args.threshold!r}")
        return 2

    mode = (args.mode or "warn").strip().lower()
    if mode not in ("warn", "fail"):
        print(f"ERROR: --mode must be 'warn' or 'fail', got: {mode!r}")
        return 2

    norm = normalize(score, threshold)
    passed, margin = verdict(norm.score_100, norm.threshold_100)

    print_header()
    print_inputs(score, threshold, mode, norm)
    print_result(passed, norm, margin, mode)

    # Exit behavior
    if mode == "warn":
        return 0
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
