import argparse
import os
import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path

DEFAULT_THRESHOLD = 0.80
DEFAULT_CONFIG_PATH = ".godscore.yml"
RUN_LOG_PATH = Path("gv_runs.jsonl")


# -----------------------------
# Helpers
# -----------------------------

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

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data if isinstance(data, dict) else {}


def resolve_threshold(config_path: str) -> float:
    # Priority: ENV → YAML → DEFAULT
    env_val = _coerce_float(os.getenv("GV_THRESHOLD"))
    if env_val is not None:
        return env_val

    cfg = _try_load_yaml(config_path)
    gv_cfg = cfg.get("gv", {})
    yaml_val = _coerce_float(gv_cfg.get("threshold"))
    if yaml_val is not None:
        return yaml_val

    return DEFAULT_THRESHOLD


def write_run_log(score: float, threshold: float, passed: bool) -> None:
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "score": score,
        "threshold": threshold,
        "passed": passed,
    }

    with RUN_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def write_step_summary(score: float, threshold: float, passed: bool) -> None:
    """
    PRO FEATURE:
    Writes a GitHub Actions step summary if GODSCORE_PRO=true
    """
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    status = "✅ PASS" if passed else "❌ FAIL"
    delta = score - threshold

    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("## GodScore CI Summary\n\n")
        f.write(f"- **Score:** `{score:.3f}`\n")
        f.write(f"- **Threshold:** `{threshold:.3f}`\n")
        f.write(f"- **Result:** {status}\n")
        f.write(f"- **Delta:** `{delta:+.3f}`\n\n")

        if delta < 0:
            f.write("⚠️ **Survivability regression detected.**\n")


def enforce_gv(score: float, threshold: float) -> None:
    if score < threshold:
        print(
            f"❌ GodScore CI gate failed: score {score:.3f} < threshold {threshold:.3f}"
        )
        sys.exit(1)

    print(
        f"✅ GodScore CI gate passed: score {score:.3f} ≥ threshold {threshold:.3f}"
    )


# -----------------------------
# Main
# -----------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="GodScore CI gate")
    parser.add_argument("--score", type=float, help="God Variable score")
    parser.add_argument("--threshold", type=float, help="Override threshold")
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Path to .godscore.yml",
    )

    args = parser.parse_args()

    # Resolve score
    score = args.score
    if score is None:
        score = _coerce_float(os.getenv("GV_SCORE"))

    if score is None:
        print("❌ Missing Gv score. Provide --score or set GV_SCORE.")
        return 2

    # Resolve threshold
    threshold = (
        args.threshold
        if args.threshold is not None
        else resolve_threshold(args.config)
    )

    passed = score >= threshold

    # Always log history (free + pro)
    write_run_log(score, threshold, passed)

    # PRO-only summary
    if os.getenv("GODSCORE_PRO", "").lower() == "true":
        write_step_summary(score, threshold, passed)

    # Enforce gate
    enforce_gv(score, threshold)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

