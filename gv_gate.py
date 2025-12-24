import argparse
import os
import sys
import json
from typing import Any, Dict, Optional, List
from datetime import datetime
from pathlib import Path

# ----------------------------
# Defaults
# ----------------------------
DEFAULT_THRESHOLD = 0.80
DEFAULT_CONFIG_PATH = ".godscore.yml"
DEFAULT_MODE = "free"  # free | pro
DEFAULT_HISTORY_WINDOW = 5
DEFAULT_MAX_REGRESSION = 0.02  # allowed drop vs recent baseline average

RUN_LOG_PATH = Path("gv_runs.jsonl")

# ----------------------------
# Helpers
# ----------------------------
def _coerce_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None

def _coerce_int(x: Any) -> Optional[int]:
    try:
        return int(x)
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

def _append_run_log(record: Dict[str, Any]) -> None:
    record = dict(record)
    record["timestamp"] = datetime.utcnow().isoformat() + "Z"
    with RUN_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def _read_run_history(limit: int = 50) -> List[Dict[str, Any]]:
    if not RUN_LOG_PATH.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with RUN_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows[-limit:]

def _avg(nums: List[float]) -> Optional[float]:
    nums = [n for n in nums if isinstance(n, (int, float))]
    if not nums:
        return None
    return sum(nums) / len(nums)

def write_step_summary(score: float, threshold: float, passed: bool, extra_lines: List[str] | None = None) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    status = "✅ PASS" if passed else "❌ FAIL"
    delta = score - threshold
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("## GodScore CI Summary\n\n")
        f.write(f"- **Score:** `{score:.3f}`\n")
        f.write(f"- **Threshold:** `{threshold:.3f}`\n")
        f.write(f"- **Result:** **{status}**\n")
        f.write(f"- **Delta:** `{delta:+.3f}`\n")
        if extra_lines:
            f.write("\n")
            for line in extra_lines:
                f.write(f"{line}\n")

# ----------------------------
# Core gate logic
# ----------------------------
def resolve_threshold(cli_threshold: Optional[float], config_path: str) -> float:
    if cli_threshold is not None:
        return float(cli_threshold)

    cfg = _try_load_yaml(config_path)
    # supports: threshold: 0.80 OR gv: { threshold: 0.80 }
    t = None
    if "threshold" in cfg:
        t = _coerce_float(cfg.get("threshold"))
    elif isinstance(cfg.get("gv"), dict):
        t = _coerce_float(cfg["gv"].get("threshold"))

    return float(t) if t is not None else DEFAULT_THRESHOLD

def enforce_gate(score: float, threshold: float) -> bool:
    return score >= threshold

def pro_regression_check(score: float, history_window: int, max_regression: float) -> Optional[str]:
    """
    Compare current score to average of recent scores.
    If score is more than max_regression below baseline avg, flag it.
    """
    history = _read_run_history(limit=200)
    recent_scores: List[float] = []
    for r in reversed(history):
        s = r.get("score")
        if isinstance(s, (int, float)):
            recent_scores.append(float(s))
        if len(recent_scores) >= history_window:
            break

    baseline = _avg(recent_scores) if recent_scores else None
    if baseline is None:
        return None

    drop = baseline - score
    if drop > max_regression:
        return f"🚨 **PRO regression:** current `{score:.3f}` vs baseline `{baseline:.3f}` (drop `{drop:.3f}` > allowed `{max_regression:.3f}`)"
    return None

def require_pro_token(mode: str, token: Optional[str]) -> Optional[str]:
    """
    Require token for pro mode. Token can be passed or via env GV_PRO_TOKEN.
    """
    if mode != "pro":
        return None
    effective = token or os.getenv("GV_PRO_TOKEN")
    if not effective:
        return "❌ PRO mode requires a token. Provide `--token ...` or set env `GV_PRO_TOKEN`."
    return None

# ----------------------------
# CLI
# ----------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GodScore CI gate (Gv).")
    p.add_argument("--score", type=float, required=True, help="Current Gv score for this run.")
    p.add_argument("--threshold", type=float, default=None, help="Minimum allowed Gv score.")
    p.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to config YAML.")
    p.add_argument("--mode", type=str, default=DEFAULT_MODE, choices=["free", "pro"], help="free | pro")
    p.add_argument("--token", type=str, default=None, help="PRO token (or set env GV_PRO_TOKEN).")

    # pro-only knobs (still safe defaults)
    p.add_argument("--history-window", type=int, default=DEFAULT_HISTORY_WINDOW, help="PRO: baseline window size.")
    p.add_argument("--max-regression", type=float, default=DEFAULT_MAX_REGRESSION, help="PRO: allowed drop vs baseline avg.")
    return p

def main() -> int:
    args = build_parser().parse_args()

    score = float(args.score)

    # PRO lock
    token_err = require_pro_token(args.mode, args.token)
    if token_err:
        print(token_err)
        _append_run_log({"score": score, "threshold": None, "passed": False, "mode": args.mode, "reason": "missing_pro_token"})
        write_step_summary(score, threshold=0.0, passed=False, extra_lines=[token_err])
        return 3

    threshold = resolve_threshold(args.threshold, args.config)
    passed = enforce_gate(score, threshold)

    extra: List[str] = []
    reason = "ok"

    # PRO regression check
    if args.mode == "pro":
        msg = pro_regression_check(score, int(args.history_window), float(args.max_regression))
        if msg:
            extra.append(msg)
            passed = False
            reason = "pro_regression"

    _append_run_log(
        {
            "score": score,
            "threshold": threshold,
            "passed": passed,
            "mode": args.mode,
            "history_window": int(args.history_window),
            "max_regression": float(args.max_regression),
            "reason": reason,
        }
    )

    write_step_summary(score, threshold, passed, extra_lines=extra if extra else None)

    if passed:
        print(f"✅ PASS: score {score:.3f} >= threshold {threshold:.3f}")
        return 0

    print(f"❌ FAIL: score {score:.3f} < threshold {threshold:.3f}" if reason == "ok" else "❌ FAIL: PRO regression check failed")
    for line in extra:
        print(line)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
