import argparse
import os
import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path

# ----------------------------
# Defaults
# ----------------------------

DEFAULT_THRESHOLD = 0.80
DEFAULT_CONFIG_PATH = ".godscore.yml"
DEFAULT_MODE = "free"  # free | pro
RUN_LOG_PATH = Path("gv_runs.jsonl")

# ----------------------------
# Helpers
# ----------------------------

def _coerce_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def _try_load_yaml(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def resolve_threshold(config: Dict[str, Any]) -> float:
    val = _coerce_float(config.get("threshold"))
    return val if val is not None else DEFAULT_THRESHOLD


def resolve_mode(config: Dict[str, Any]) -> str:
    mode = config.get("mode")
    if mode in ("free", "pro"):
        return mode
    return DEFAULT_MODE


# ----------------------------
# Output & Logging
# ----------------------------

def write_run_log(score: float, threshold: float, passed: bool, mode: str) -> None:
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "score": score,
        "threshold": threshold,
        "passed": passed,
        "mode": mode,
    }
    with RUN_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def write_step_summary(score: float, threshold: float, passed: bool, mode: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    status = "✅ PASS" if passed else "❌ FAIL"
    delta = score - threshold

    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("## GodScore CI Summary\n\n")
        f.write(f"- **Mode:** {mode.upper()}\n")
        f.write(f"- **Score:** {score:.3f}\n")
        f.write(f"- **Threshold:** {threshold:.3f}\n")
        f.write(f"- **Result:** {status}\n")
        f.write(f"- **Delta:** {delta:+.3f}\n")
        if delta < 0:
            f.write("\n⚠️ **Survivability regression detected.**\n")


# ----------------------------
# Core Enforcement
# ----------------------------

def enforce_gv(score: float, threshold: float, mode: str) -> None:
    passed = score >= threshold

    write_run_log(score, threshold, passed, mode)
    write_step_summary(score, threshold, passed, mode)

    if not passed:
        print(f"❌ God Variable gate failed ({score:.3f} < {threshold:.3f})")
        sys.exit(1)

    print(f"✅ God Variable gate passed ({score:.3f} ≥ {threshold:.3f})")


# ----------------------------
# Main
# ----------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="GodScore CI – Survivability Gate")
    parser.add_argument("--score", help="God Variable score", type=float)
    parser.add_argument("--threshold", help="Override threshold", type=float)
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Config file path")

    args = parser.parse_args()

    config = _try_load_yaml(args.config)
    mode = resolve_mode(config)

    print("✨ GodScore CI running in PRO mode" if mode == "pro" else "🔓 GodScore CI running in FREE mode")

    score = args.score
    if score is None:
        score = _coerce_float(os.getenv("GV_SCORE"))

    if score is None:
        print("❌ Missing Gv score. Provide --score or set GV_SCORE.")
        return 2

    threshold = args.threshold if args.threshold is not None else resolve_threshold(config)

    enforce_gv(score, threshold, mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
