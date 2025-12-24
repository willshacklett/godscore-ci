import argparse
import os
import sys
from typing import Any, Dict, Optional


DEFAULT_THRESHOLD = 0.80
DEFAULT_CONFIG_PATH = ".godscore.yml"


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
    if not isinstance(data, dict):
        return {}
    return data


def _coerce_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def resolve_threshold(config_path: str) -> float:
    """
    Priority:
      1) CLI --threshold
      2) ENV GV_THRESHOLD
      3) Config file .godscore.yml -> gv.threshold
      4) DEFAULT_THRESHOLD
    """
    cfg = _try_load_yaml(config_path)
    cfg_threshold = None
    if isinstance(cfg.get("gv"), dict):
        cfg_threshold = _coerce_float(cfg["gv"].get("threshold"))

    env_threshold = _coerce_float(os.getenv("GV_THRESHOLD"))

    # caller will override via CLI; handled in main()
    return env_threshold if env_threshold is not None else (cfg_threshold if cfg_threshold is not None else DEFAULT_THRESHOLD)


def enforce_gv(score: float, threshold: float) -> None:
    if score < threshold:
        print(f"❌ Gv gate failed: score={score:.4f} < threshold={threshold:.4f}")
        sys.exit(1)
    print(f"✅ Gv gate passed: score={score:.4f} ≥ threshold={threshold:.4f}")


def main() -> int:
    parser = argparse.ArgumentParser(description="God Variable (Gv) CI gate.")
    parser.add_argument("--score", type=float, default=None, help="Gv score to evaluate (required unless GV_SCORE is set).")
    parser.add_argument("--threshold", type=float, default=None, help="Minimum allowed Gv (overrides config/env).")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to .godscore.yml config.")
    args = parser.parse_args()

    # Score: CLI -> ENV
    score = args.score
    if score is None:
        score = _coerce_float(os.getenv("GV_SCORE"))
    if score is None:
        print("❌ Missing score. Provide --score <float> or set GV_SCORE.")
        return 2

    # Threshold: CLI -> ENV/CONFIG -> default
    threshold = args.threshold if args.threshold is not None else resolve_threshold(args.config)

    enforce_gv(score, threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
