#!/usr/bin/env python3
"""
gv_gate.py — God Variable trajectory gate (CI-friendly)

What it does:
- Reads a CSV with a 'date' column + metric columns
- For each metric, computes:
  - trend slope (linear regression)
  - acceleration (2nd difference)
  - variance drift (rolling variance slope)
- Converts those into a *risk* score per metric (higher risk = worse)
- Aggregates into a single Gv score in [0,1] (higher = healthier)
- Exits 1 if Gv < threshold (perfect for GitHub Actions)

Key upgrades vs what you pasted:
- NaN-safe
- Supports per-metric direction: higher-is-better OR lower-is-better
- Only penalizes *degradation* (won't punish improvements)
- Weights + directions via a single JSON config
"""

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
from scipy.stats import linregress


@dataclass
class MetricConfig:
    weight: float = 1.0
    direction: str = "higher"  # "higher" or "lower"


def _safe_linregress(x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    # linregress needs >=2 points
    if len(y) < 2:
        return {"slope": 0.0, "r2": 0.0}
    res = linregress(x, y)
    return {"slope": float(res.slope), "r2": float(res.rvalue**2)}


def compute_trajectory_dynamics(series: pd.Series, window: int = 5) -> Dict[str, Any]:
    s = series.dropna()
    if len(s) < 3:
        return {"valid": False, "reason": "insufficient points", "points": int(len(s))}

    y = s.values.astype(float)
    x = np.arange(len(y), dtype=float)

    reg = _safe_linregress(x, y)
    slope = reg["slope"]
    r2 = reg["r2"]

    diffs = np.diff(y)
    accel = float(np.mean(np.diff(diffs))) if len(diffs) > 1 else 0.0

    w = min(window, len(s))
    roll_var = s.rolling(window=w).var().dropna()
    if len(roll_var) >= 3:
        xv = np.arange(len(roll_var), dtype=float)
        var_reg = _safe_linregress(xv, roll_var.values.astype(float))
        var_drift = var_reg["slope"]
    else:
        var_drift = 0.0

    return {
        "valid": True,
        "points": int(len(s)),
        "trend_slope": float(slope),
        "loss_acceleration": float(accel),
        "variance_drift_slope": float(var_drift),
        "current_value": float(s.iloc[-1]),
        "baseline_value": float(s.iloc[0]),
        "r_squared": float(round(r2, 4)),
    }


def parse_config(config_str: str, metric_names: list[str]) -> Dict[str, MetricConfig]:
    """
    config_str can be:
      - "equal"
      - JSON dict:
          {
            "mmlu": {"weight": 2, "direction": "higher"},
            "loss": {"weight": 3, "direction": "lower"},
            "latency_ms": {"weight": 1.5, "direction": "lower"}
          }
        Or shorthand:
          {"mmlu": 2, "loss": 3}
        (direction defaults to "higher")
    """
    if config_str == "equal":
        return {m: MetricConfig() for m in metric_names}

    raw = json.loads(config_str)
    cfg: Dict[str, MetricConfig] = {}

    for m in metric_names:
        if m not in raw:
            cfg[m] = MetricConfig()
            continue

        val = raw[m]
        if isinstance(val, (int, float)):
            cfg[m] = MetricConfig(weight=float(val), direction="higher")
        elif isinstance(val, dict):
            weight = float(val.get("weight", 1.0))
            direction = str(val.get("direction", "higher")).lower().strip()
            if direction not in ("higher", "lower"):
                raise ValueError(f"Invalid direction for '{m}': {direction}. Use 'higher' or 'lower'.")
            cfg[m] = MetricConfig(weight=weight, direction=direction)
        else:
            raise ValueError(f"Invalid config value for metric '{m}': {val}")

    return cfg


def _orient_series_for_scoring(series: pd.Series, direction: str) -> pd.Series:
    # Convert all metrics to a unified "higher is better" orientation for scoring
    if direction == "higher":
        return series
    if direction == "lower":
        return -series
    # Should never happen due to validation
    return series


def metric_risk_from_dynamics(dyn: Dict[str, Any],
                              k_slope: float,
                              k_accel: float,
                              k_var: float) -> float:
    """
    Risk is >= 0. Higher risk means the metric is degrading:
      - negative trend slope increases risk
      - negative acceleration (decline speeding up) increases risk
      - positive variance drift increases risk
    Assumes dyn was computed on oriented series where "higher is better".
    """
    if not dyn.get("valid", False):
        return 0.0

    slope = float(dyn["trend_slope"])
    accel = float(dyn["loss_acceleration"])
    var_drift = float(dyn["variance_drift_slope"])

    # Only penalize *degradation*
    slope_risk = max(0.0, -slope)           # downward trend = risk
    accel_risk = max(0.0, -accel)           # decline speeding up = risk
    var_risk = max(0.0, var_drift)          # increasing instability = risk

    # Weighted sum in "risk space"
    risk = (k_slope * slope_risk) + (k_accel * accel_risk) + (k_var * var_risk)
    return float(risk)


def gv_from_weighted_risk(weighted_risk_sum: float, total_weight: float, alpha: float) -> float:
    """
    Convert risk -> Gv in [0,1] using a smooth, tunable mapping.
    Higher alpha => harsher penalty for risk.
    """
    if total_weight <= 0:
        return 1.0
    avg_risk = weighted_risk_sum / total_weight
    gv = 1.0 / (1.0 + alpha * avg_risk)
    return float(max(0.0, min(1.0, gv)))


def main() -> None:
    p = argparse.ArgumentParser(description="Gv trajectory gate – constraint-field monitor for system/AI metrics")
    p.add_argument("input_csv", help="CSV with a 'date' column + metric columns")
    p.add_argument("--threshold", type=float, default=0.80, help="Fail if Gv < threshold (default: 0.80)")
    p.add_argument(
        "--config",
        type=str,
        default="equal",
        help=("Metric config JSON or 'equal'. Example: "
              r"""'{"mmlu":{"weight":2,"direction":"higher"},"loss":{"weight":3,"direction":"lower"}}'"""),
    )
    p.add_argument("--window", type=int, default=5, help="Rolling variance window (default: 5)")
    p.add_argument("--alpha", type=float, default=10.0, help="Risk-to-Gv sensitivity (default: 10.0)")
    p.add_argument("--k_slope", type=float, default=10.0, help="Slope risk multiplier (default: 10.0)")
    p.add_argument("--k_accel", type=float, default=50.0, help="Acceleration risk multiplier (default: 50.0)")
    p.add_argument("--k_var", type=float, default=20.0, help="Variance drift risk multiplier (default: 20.0)")
    p.add_argument("--output", choices=["human", "json"], default="human")
    args = p.parse_args()

    df = pd.read_csv(args.input_csv, parse_dates=["date"])
    if "date" not in df.columns:
        raise SystemExit("CSV must include a 'date' column.")

    df = df.sort_values("date")
    metric_cols = [c for c in df.columns if c != "date"]
    if not metric_cols:
        raise SystemExit("CSV must include at least one metric column besides 'date'.")

    cfg = parse_config(args.config, metric_cols)

    per_metric = []
    weighted_risk_sum = 0.0
    total_weight = 0.0

    for m in metric_cols:
        oriented = _orient_series_for_scoring(df[m], cfg[m].direction)
        dyn = compute_trajectory_dynamics(oriented, window=args.window)
        dyn["metric"] = m
        dyn["direction"] = cfg[m].direction
        dyn["weight"] = float(cfg[m].weight)

        risk = metric_risk_from_dynamics(dyn, args.k_slope, args.k_accel, args.k_var)
        dyn["risk"] = float(round(risk, 6))

        if dyn.get("valid", False):
            weighted_risk_sum += risk * cfg[m].weight
            total_weight += cfg[m].weight

        per_metric.append(dyn)

    gv = gv_from_weighted_risk(weighted_risk_sum, total_weight, alpha=args.alpha)
    gv = float(round(gv, 4))

    report = {
        "god_variable_score": gv,
        "threshold": float(args.threshold),
        "pass": bool(gv >= args.threshold),
        "alpha": float(args.alpha),
        "k_slope": float(args.k_slope),
        "k_accel": float(args.k_accel),
        "k_var": float(args.k_var),
        "window": int(args.window),
        "metrics": per_metric,
    }

    if args.output == "json":
        print(json.dumps(report, indent=2))
    else:
        status = "PASS" if report["pass"] else "FAIL – IRREVERSIBILITY RISK"
        print(f"Gv Score: {gv}")
        print(f"Threshold: {args.threshold} → {status}")
        print("")
        print("Per-metric dynamics (oriented so 'higher is better'):")
        for d in per_metric:
            if not d.get("valid", False):
                print(f"  {d['metric']}: invalid ({d.get('reason','')})")
                continue
            print(
                f"  {d['metric']} [{d['direction']} w={d['weight']}]: "
                f"slope={d['trend_slope']:.6f}, accel={d['loss_acceleration']:.6f}, "
                f"var_drift={d['variance_drift_slope']:.6f}, risk={d['risk']:.6f}, r2={d['r_squared']}"
            )

    if not report["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
