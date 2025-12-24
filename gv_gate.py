import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# -------------------------
# Defaults
# -------------------------

DEFAULT_THRESHOLD = 0.80
DEFAULT_CONFIG_PATH = ".godscore.yml"
RUN_LOG_PATH = Path("gv_runs.jsonl")

# -------------------------
# Utilities
# -------------------------

def _try_load_yaml(path: str) -> Dict[str, Any]:
    """
    Optional YAML config loader.
    If PyYAML isn't installed or file doesn't exist, returns {}.
    """
    if not os.path.exists(path):
        return {}

    try:
        import yaml  # type: ignore
    except Exception:
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data if isinstance(data, dict) else {}


def _coerce_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def resolve_threshold(config_path: str) -> float:
    """
    Threshold resolution priority:
      1) ENV: GV_THRESHOLD
      2) Config file: .godscore.yml → gv.threshold
      3) DEFAULT_THRESHOLD
    """
    cfg = _try_load_yaml(config_path)
    cfg_threshold = None

    if isinstance(cfg.get("gv"), dict):
        cfg_threshold = _coerce_float(cfg["gv"].get("threshold"))

    env_threshold = _coerce_float(os.getenv("GV_THRESHOLD"))

    if env_threshold is not None:
        return env_threshold
    if cfg_threshold is not None:
        return cfg_threshold
    return DEFAULT_THRESHOLD

# -------------------------
# Learning Hook
# -------------------------

def write_run_log(score: float, threshold: float, passed: bool) -> None:
    """
    Append a single Gv evaluation record to a local JSONL log.
    """
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "score": score,
        "threshold": threshold,
        "passed": passed,
    }

    with RUN_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

# -------------------------
# Gate Enforcement
# -------------------------

def enforce_gv(score: float, threshold: float) -> None:
    passed = score >= threshold

    # Learning hook fires on every run
    write_run_log(score, threshold, passed)

    if not passed:
        print(f"❌ Gv gate failed: score={score:.4f} < threshold={threshold:.4f}")
        sys.exit(1)

    print(f"✅ Gv gate passed: score={score:.4f} ≥ threshold={threshold:.4f}")

# -------------------------
# CLI Entry Point
# -------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="God Variable (Gv) CI gate")
    parser.add_argument(
        "--score",
        type=float,
        default=None,
        help="Gv score to evaluate (or set GV_SCORE env var)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Override threshold (highest priority)",
    )
    parser.add_argument(
        "--config",
        type=str,
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
    threshold = args.threshold if args.threshold is not None else resolve_threshold(args.config)

    enforce_gv(score, threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
