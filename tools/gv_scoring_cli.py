#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
from scipy.stats import linregress
import json
import sys

def compute_trajectory_dynamics(series: pd.Series) -> dict:
    if len(series) < 3:
        return {"valid": False, "reason": "insufficient points"}
    
    # Primary margin loss slope
    x = np.arange(len(series))
    slope, intercept, r_value, p_value, std_err = linregress(x, series.values)
    
    # Acceleration (second difference approximation)
    diffs = np.diff(series.values)
    accel = np.mean(np.diff(diffs)) if len(diffs) > 1 else 0.0
    
    # Variance drift
    window_variance = series.rolling(window=min(5, len(series))).var().dropna()
    variance_trend = linregress(np.arange(len(window_variance)), window_variance.values).slope if len(window_variance) > 1 else 0.0
    
    return {
        "valid": True,
        "points": len(series),
        "margin_loss_slope": round(slope, 6),
        "loss_acceleration": round(accel, 6),
        "variance_drift_slope": round(variance_trend, 6),
        "current_value": float(series.iloc[-1]),
        "baseline_value": float(series.iloc[0]),
        "r_squared": round(r_value**2, 4)
    }

def compute_gv_score(dynamics: list[dict], weights: dict) -> float:
    # Simple weighted Gv: higher = healthier field
    score = 0.0
    total_weight = sum(weights.values())
    for dyn in dynamics:
        if not dyn["valid"]:
            continue
        # Negative slopes drag Gv down; acceleration penalizes heavily
        metric_score = (
            -10 * abs(dyn["margin_loss_slope"])  # primary degradation
            - 50 * max(0, -dyn["loss_acceleration"])  # accelerating loss = irreversibility precursor
            - 20 * max(0, dyn["variance_drift_slope"])  # destabilization
        )
        score += metric_score * weights.get(dyn["metric"], 1.0)
    return round(1.0 / (1.0 + abs(score / total_weight)), 4)  # normalize to ~[0,1]

def main():
    parser = argparse.ArgumentParser(description="God Variable trajectory scorer – constraint-field monitor for AI/system metrics")
    parser.add_argument("input_csv", help="CSV with 'date' column + metric columns (e.g., mmlu, gpqa, safety)")
    parser.add_argument("--threshold", type=float, default=0.80, help="Gv failure threshold (default 0.80)")
    parser.add_argument("--weights", type=str, default="equal", help="JSON weights {'mmlu':2.0,'safety':3.0} or 'equal'")
    parser.add_argument("--output", choices=["json", "human"], default="human")
    args = parser.parse_args()
    
    df = pd.read_csv(args.input_csv, parse_dates=["date"])
    df = df.sort_values("date")
    
    weights = json.loads(args.weights) if args.weights != "equal" else {col: 1.0 for col in df.columns if col != "date"}
    
    dynamics = []
    for col in df.columns:
        if col == "date":
            continue
        dyn = compute_trajectory_dynamics(df[col])
        dyn["metric"] = col
        dynamics.append(dyn)
    
    gv = compute_gv_score(dynamics, weights)
    
    report = {
        "god_variable_score": gv,
        "threshold": args.threshold,
        "pass": gv >= args.threshold,
        "trajectory_dynamics": dynamics
    }
    
    if args.output == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"God Variable (Gv) Score: {gv}")
        print(f"Threshold: {args.threshold} → {'PASS' if report['pass'] else 'FAIL – IRREVERSIBILITY RISK'}")
        print("\nPer-metric dynamics:")
        for d in dynamics:
            if d["valid"]:
                print(f"  {d['metric']}: slope={d['margin_loss_slope']}, accel={d['loss_acceleration']}, var_drift={d['variance_drift_slope']}")
    
    if not report["pass"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
