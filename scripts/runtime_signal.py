from __future__ import annotations

import argparse
import json
from pathlib import Path
import os

import numpy as np
import pandas as pd


def first_true(v):
    idx = np.flatnonzero(v)
    return int(idx[0]) if len(idx) else None


def rolling_slope(s, w=10):
    out = []
    vals = s.astype(float).values
    for i in range(len(vals)):
        y = vals[max(0, i - w + 1): i + 1]
        if len(y) < 3:
            out.append(0.0)
            continue
        x = np.arange(len(y), dtype=float)
        out.append(float(np.polyfit(x, y, 1)[0]))
    return pd.Series(out, index=s.index)


def compute_runtime_signal(df: pd.DataFrame):
    x = df["metric"].astype(float)
    t = df["t"]

    dsdt = x.diff().fillna(0.0)

    dsdt_med = dsdt.rolling(20, min_periods=5).median().fillna(0.0)
    dsdt_mad = (dsdt - dsdt_med).abs().rolling(20, min_periods=5).median().fillna(0.0)
    adaptive_thr = dsdt_med + 2.2 * (1.4826 * dsdt_mad + 0.003)
    spike = dsdt > adaptive_thr

    d2sdt = dsdt.diff().fillna(0.0)
    vel_decay = d2sdt < -0.002
    spike = spike & (~vel_decay)

    persistence = spike.astype(float).rolling(16, min_periods=1).mean().fillna(0.0)

    baseline = x.rolling(30, min_periods=5).mean()
    deviation = (x - baseline).abs().fillna(0.0)
    dev_norm = (deviation / 0.08).clip(0, 3) / 3.0

    slope = rolling_slope(x, 10)
    slope_norm = (slope.clip(lower=0.0) / 0.01).clip(0, 1)

    rec_fail = ((deviation > 0.08) & (slope > 0)).astype(float)

    lag_vals = []
    cur = 0.0
    for v in rec_fail:
        if v:
            cur = min(1.0, 0.82 * cur + 0.28)
        else:
            cur = max(0.0, 0.82 * cur - 0.02)
        lag_vals.append(cur)
    lag = pd.Series(lag_vals, index=df.index)

    gv = (
        0.18 * spike.astype(float)
        + 0.24 * persistence
        + 0.18 * dev_norm
        + 0.18 * slope_norm
        + 0.22 * lag
    )

    warned = (gv >= 0.65) & ((persistence >= 0.35) | (lag >= 0.20))

    first = first_true(warned.values)

    enriched = df.copy()
    enriched["dsdt"] = dsdt
    enriched["adaptive_threshold"] = adaptive_thr
    enriched["spike_candidate"] = spike.astype(int)
    enriched["persistence"] = persistence
    enriched["deviation"] = deviation
    enriched["slope"] = slope
    enriched["recovery_lag"] = lag
    enriched["gv_signal"] = gv
    enriched["warning"] = warned.astype(int)

    max_gv = float(gv.max())
    max_persistence = float(persistence.max())
    max_lag = float(lag.max())
    warned_any = bool(warned.any())

    risk = float(np.clip(max(max_gv, max_lag), 0.0, 1.0))
    godscore = int(round(100 * (1.0 - risk)))

    summary = {
        "rows": int(len(df)),
        "warned": warned_any,
        "first_warning_t": None if first is None else int(t.iloc[first]),
        "max_gv": max_gv,
        "max_persistence": max_persistence,
        "max_lag": max_lag,
        "godscore_runtime": godscore,
        "effective_mode": "advisory",
    }
    return enriched, summary


def emit_github_outputs(summary: dict):
    output_path = os.environ.get("GITHUB_OUTPUT", "")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"warned={'true' if summary['warned'] else 'false'}\n")
        f.write(f"first_warning_t={summary['first_warning_t']}\n")
        f.write(f"max_gv={summary['max_gv']:.6f}\n")
        f.write(f"max_persistence={summary['max_persistence']:.6f}\n")
        f.write(f"max_lag={summary['max_lag']:.6f}\n")
        f.write(f"godscore_runtime={summary['godscore_runtime']}\n")
        f.write(f"effective_mode={summary['effective_mode']}\n")


def main():
    ap = argparse.ArgumentParser(description="Runtime irreversibility signal for GodScore-CI.")
    ap.add_argument("csv", help="Input CSV with columns: t, metric")
    ap.add_argument("--outdir", default="outputs/runtime_signal")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    required = {"t", "metric"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    enriched, summary = compute_runtime_signal(df)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    stem = Path(args.csv).stem
    enriched_path = outdir / f"{stem}_enriched.csv"
    summary_path = outdir / f"{stem}_summary.json"

    enriched.to_csv(enriched_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2))

    print("")
    print("=== RUNTIME SIGNAL SUMMARY ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    print("")
    print("Wrote:")
    print(f" - {enriched_path}")
    print(f" - {summary_path}")

    emit_github_outputs(summary)


if __name__ == "__main__":
    main()
