import json
from pathlib import Path

HISTORY = Path("outputs/runtime_signal/runtime_history.jsonl")
OUT = Path("outputs/runtime_signal/runtime_drift_summary.json")

if not HISTORY.exists():
    raise SystemExit("Missing runtime history file: outputs/runtime_signal/runtime_history.jsonl")

rows = []
for line in HISTORY.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line:
        rows.append(json.loads(line))

if not rows:
    raise SystemExit("Runtime history is empty")

if len(rows) < 2:
    summary = {
        "enough_history": False,
        "drift_detected": False,
        "reason": "Not enough history",
        "latest_score": rows[-1]["score"],
        "score_slope": 0.0,
        "warn_count_recent": sum(1 for r in rows if r.get("warned")),
    }
else:
    scores = [r.get("score", 100) for r in rows]
    warns = [bool(r.get("warned", False)) for r in rows]

    first_score = scores[0]
    last_score = scores[-1]
    n = len(scores)
    score_slope = (last_score - first_score) / max(1, n - 1)

    recent_window = rows[-3:] if len(rows) >= 3 else rows
    warn_count_recent = sum(1 for r in recent_window if r.get("warned"))

    drift_detected = False
    reasons = []

    if score_slope <= -3:
        drift_detected = True
        reasons.append(f"score_slope={score_slope:.2f}")

    if warn_count_recent >= 2:
        drift_detected = True
        reasons.append(f"warn_count_recent={warn_count_recent}")

    if last_score < 50:
        drift_detected = True
        reasons.append(f"latest_score={last_score}")

    summary = {
        "enough_history": True,
        "drift_detected": drift_detected,
        "reason": ", ".join(reasons) if reasons else "stable",
        "latest_score": last_score,
        "score_slope": score_slope,
        "warn_count_recent": warn_count_recent,
    }

OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

print("")
print("=== RUNTIME DRIFT SUMMARY ===")
for k, v in summary.items():
    print(f"{k}: {v}")
print("")
print(f"Wrote: {OUT}")
