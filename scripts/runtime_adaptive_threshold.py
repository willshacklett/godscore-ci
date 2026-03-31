import json
from pathlib import Path

HISTORY = Path("outputs/runtime_signal/runtime_history.jsonl")
OUT = Path("outputs/runtime_signal/runtime_adaptive_summary.json")

rows = []
for line in HISTORY.read_text().splitlines():
    if line.strip():
        rows.append(json.loads(line))

scores = [r.get("score", 100) for r in rows]

if len(scores) < 2:
    volatility = 0
else:
    diffs = [abs(scores[i] - scores[i-1]) for i in range(1, len(scores))]
    volatility = sum(diffs) / len(diffs)

# Adaptive threshold logic
base_threshold = 50

if volatility > 10:
    threshold = base_threshold - 10   # more tolerance
elif volatility < 3:
    threshold = base_threshold + 5    # stricter
else:
    threshold = base_threshold

latest_score = scores[-1]

summary = {
    "latest_score": latest_score,
    "volatility": volatility,
    "adaptive_threshold": threshold,
    "fail": latest_score < threshold
}

OUT.write_text(json.dumps(summary, indent=2))

print("")
print("=== ADAPTIVE THRESHOLD SUMMARY ===")
for k, v in summary.items():
    print(f"{k}: {v}")
print("")
print(f"Wrote: {OUT}")
