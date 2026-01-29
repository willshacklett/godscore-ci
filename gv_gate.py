import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ----------------------------
# Defaults
# ----------------------------

DEFAULT_THRESHOLD = 0.80
DEFAULT_CONFIG_PATH = ".godscore.yml"

# Canonical modes (what the action.yml now uses)
# warn = advisory (never fail)
# fail = enforcement (fail build on violations)
DEFAULT_MODE = "warn"  # warn | fail

# Backward-compatible legacy modes
LEGACY_FREE = "free"
LEGACY_PRO = "pro"

DEFAULT_HISTORY_WINDOW = 5
DEFAULT_MAX_REGRESSION = 0.02  # allowed drop vs recent baseline average

DEFAULT_RUN_LOG = Path("gv_runs.jsonl")

# Exit codes (kept stable & explicit)
EXIT_OK = 0
EXIT_BAD_INPUT = 2
EXIT_PRO_TOKEN_MISSING = 3  # reserved (not used by warn/fail)
EXIT_THRESHOLD_FAIL = 4
EXIT_REGRESSION_FAIL = 5


# ----------------------------
# Helpers
# ----------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        # YAML dependency may not be installed in some contexts
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def resolve_threshold(config_path: str) -> float:
    cfg = _try_load_yaml(config_path)
    # Accept a few common shapes:
    # threshold: 0.8
    # godscore: { threshold: 0.8 }
    # gv: { threshold: 0.8 }
    candidates = [
        cfg.get("threshold"),
        (cfg.get("godscore") or {}).get("threshold") if isinstance(cfg.get("godscore"), dict) else None,
        (cfg.get("gv") or {}).get("threshold") if isinstance(cfg.get("gv"), dict) else None,
    ]
    for c in candidates:
        v = _coerce_float(c)
        if v is not None:
            return v
    return DEFAULT_THRESHOLD


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        out.append(obj)
                except Exception:
                    continue
    except Exception:
        return []
    return out


def _append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception:
        # Do not crash the gate on logging failure; still print warning
        print("⚠️  Warning: could not write run history log.")


def _compute_baseline(history: List[Dict[str, Any]], window: int) -> Optional[float]:
    """
    Baseline = average score of last N entries that:
      - have a numeric 'score'
      - have 'threshold_pass' == True (so we compare against successful behavior)
    """
    scores: List[float] = []
    for item in reversed(history):
        if len(scores) >= window:
            break

        if item.get("threshold_pass") is not True:
            continue

        s = _coerce_float(item.get("score"))
        if s is None:
            continue
        scores.append(s)

    if not scores:
        return None
    return sum(scores) / len(scores)


def _write_step_summary(score: float, threshold: float, threshold_pass: bool,
                        mode: str,
                        baseline: Optional[float],
                        max_regression: float,
                        regression_delta: Optional[float],
                        regression_pass: Optional[bool]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    status = "✅ PASS" if threshold_pass and (regression_pass is not False) else "❌ FAIL"
    lines: List[str] = []
    lines.append("## GodScore CI Summary")
    lines.append("")
    lines.append(f"- **Mode:** `{mode}`")
    lines.append(f"- **Score:** `{score:.3f}`")
    lines.append(f"- **Threshold:** `{threshold:.3f}`")
    lines.append(f"- **Threshold result:** `{'PASS' if threshold_pass else 'FAIL'}`")

    if baseline is not None:
        lines.append(f"- **Baseline (avg last N):** `{baseline:.3f}`")
        if regression_delta is not None:
            lines.append(f"- **Regression delta:** `{regression_delta:+.3f}` (allowed drop: `{max_regression:.3f}`)")
        if regression_pass is not None:
            lines.append(f"- **Regression result:** `{'PASS' if regression_pass else 'FAIL'}`")
    else:
        lines.append("- **Baseline:** `N/A` (not enough history yet)")

    lines.append(f"- **Overall:** `{status}`")
    lines.append("")

    try:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass


def _normalize_mode(raw: str) -> str:
    """
    Normalize modes to canonical: warn | fail
    Accept legacy: free -> warn, pro -> fail
    """
    m = (raw or "").strip().lower()
    if m in ("warn", "advisory"):
        return "warn"
    if m in ("fail", "enforce", "enforcement"):
        return "fail"
    if m == LEGACY_FREE:
        return "warn"
    if m == LEGACY_PRO:
        return "fail"
    # default safe
    return DEFAULT_MODE


# ----------------------------
# Gate logic
# ----------------------------

def threshold_check(score: float, threshold: float) -> bool:
    return score >= threshold


def regression_check(score: float, baseline: float, max_regression: float) -> Tuple[bool, float]:
    """
    Regression condition:
      fail if score < baseline - max_regression
    Returns (pass, delta) where delta = score - baseline
    """
    delta = score - baseline
    ok = score >= (baseline - max_regression)
    return ok, delta


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="GodScore CI gate (threshold + optional regression check).")

    parser.add_argument("--score", type=float, default=None, help="Gv score for this run.")
    parser.add_argument("--threshold", type=float, default=None, help="Override threshold. If omitted, read config.")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Config file path (YAML).")

    # Canonical mode
    parser.add_argument("--mode", type=str, default=DEFAULT_MODE,
                        help="Run mode: warn (advisory) or fail (enforcement). Legacy: free/pro accepted.")

    parser.add_argument("--history-window", type=int, default=DEFAULT_HISTORY_WINDOW,
                        help="Number of recent successful runs for baseline.")
    parser.add_argument("--max-regression", type=float, default=DEFAULT_MAX_REGRESSION,
                        help="Allowed drop vs baseline average.")
    parser.add_argument("--run-log", type=str, default=str(DEFAULT_RUN_LOG),
                        help="Path to JSONL run history log.")

    args = parser.parse_args(argv)

    # Resolve score
    score = args.score
    if score is None:
        score = _coerce_float(os.getenv("GV_SCORE"))
    if score is None:
        print("❌ Missing Gv score. Provide --score or set GV_SCORE.")
        return EXIT_BAD_INPUT

    # Resolve threshold
    threshold = args.threshold if args.threshold is not None else resolve_threshold(args.config)

    mode = _normalize_mode(args.mode)
    history_window = max(1, int(args.history_window))
    max_regression = float(args.max_regression)
    run_log = Path(args.run_log)

    # Load history for baseline
    history = _read_jsonl(run_log)
    baseline = _compute_baseline(history, window=history_window)

    threshold_pass = True
    regression_pass: Optional[bool] = None
    regression_delta: Optional[float] = None

    # ---- Threshold gate ----
    t_ok = threshold_check(score, threshold)
    if t_ok:
        print(f"✅ Threshold OK: {score:.3f} ≥ {threshold:.3f}")
    else:
        threshold_pass = False
        print(f"⚠️  GodScore {score:.3f} is below threshold {threshold:.3f}.")

        if mode == "fail":
            print("❌ Enforcement active: failing build due to low GodScore.")
            exit_code = EXIT_THRESHOLD_FAIL
            _finalize(run_log, mode, score, threshold, threshold_pass,
                      baseline, max_regression, regression_pass, regression_delta,
                      exit_code)
            return exit_code
        else:
            print("ℹ️  Advisory mode: build allowed to continue (warning only).")

    # ---- Regression check (warn: warn only; fail: hard fail) ----
    if baseline is None:
        print(f"ℹ️  Regression: not enough history yet (need up to {history_window} successful prior runs). Skipping.")
    else:
        ok, delta = regression_check(score, baseline, max_regression)
        regression_pass = ok
        regression_delta = delta

        if ok:
            print(f"✅ Regression OK: score {score:.3f} vs baseline {baseline:.3f} (delta {delta:+.3f})")
        else:
            msg = (
                f"⚠️  Regression detected: score {score:.3f} vs baseline {baseline:.3f} "
                f"(delta {delta:+.3f}, allowed drop {max_regression:.3f})"
            )

            if mode == "warn":
                print(msg)
                print("ℹ️  Advisory mode: regression is a warning (does not fail CI).")
            else:
                print("❌ " + msg.replace("⚠️  ", ""))
                exit_code = EXIT_REGRESSION_FAIL
                _finalize(run_log, mode, score, threshold, threshold_pass,
                          baseline, max_regression, regression_pass, regression_delta,
                          exit_code)
                return exit_code

    _finalize(run_log, mode, score, threshold, threshold_pass,
              baseline, max_regression, regression_pass, regression_delta,
              EXIT_OK)
    return EXIT_OK


def _finalize(run_log: Path,
              mode: str,
              score: float,
              threshold: float,
              threshold_pass: bool,
              baseline: Optional[float],
              max_regression: float,
              regression_pass: Optional[bool],
              regression_delta: Optional[float],
              exit_code: int) -> None:
    # Write GH step summary (if available)
    _write_step_summary(
        score=score,
        threshold=threshold,
        threshold_pass=threshold_pass,
        mode=mode,
        baseline=baseline,
        max_regression=max_regression,
        regression_delta=regression_delta,
        regression_pass=regression_pass,
    )

    # Append run history
    record: Dict[str, Any] = {
        "ts": _now_iso(),
        "mode": mode,
        "score": round(float(score), 6),
        "threshold": round(float(threshold), 6),
        "threshold_pass": bool(threshold_pass),
        "baseline": None if baseline is None else round(float(baseline), 6),
        "max_regression": round(float(max_regression), 6),
        "regression_pass": regression_pass,
        "regression_delta": None if regression_delta is None else round(float(regression_delta), 6),
        "exit_code": int(exit_code),
        "sha": os.getenv("GITHUB_SHA"),
        "repo": os.getenv("GITHUB_REPOSITORY"),
        "run_id": os.getenv("GITHUB_RUN_ID"),
    }
    _append_jsonl(run_log, record)


if __name__ == "__main__":
    raise SystemExit(main())
