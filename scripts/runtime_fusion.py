import json
from pathlib import Path

runtime_path = Path("outputs/runtime_signal/runtime_signal_input_summary.json")
adaptive_path = Path("outputs/runtime_signal/runtime_adaptive_summary.json")
drift_path = Path("outputs/runtime_signal/runtime_drift_summary.json")
out_path = Path("outputs/runtime_signal/runtime_fused_summary.json")

runtime = json.loads(runtime_path.read_text())
adaptive = json.loads(adaptive_path.read_text())
drift = json.loads(drift_path.read_text())

runtime_score = int(runtime.get("godscore_runtime", 100))

# Placeholder static score for now.
# Replace this later with real GodScore CI static output when you wire it directly.
static_score = 78

drift_detected = bool(drift.get("drift_detected", False))
adaptive_fail = bool(adaptive.get("fail", False))

# Fusion logic:
# - weighted blend
# - drift penalty
# - hard cap when adaptive layer says fail
fused_score = round(0.55 * static_score + 0.45 * runtime_score)

if drift_detected:
    fused_score -= 10

if adaptive_fail:
    fused_score = min(fused_score, 35)

fused_score = max(0, min(100, fused_score))

if fused_score >= 80:
    fused_status = "SAFE"
elif fused_score >= 50:
    fused_status = "AT RISK"
else:
    fused_status = "CRITICAL"

summary = {
    "static_score": static_score,
    "runtime_score": runtime_score,
    "drift_detected": drift_detected,
    "adaptive_fail": adaptive_fail,
    "fused_score": fused_score,
    "fused_status": fused_status,
}

out_path.write_text(json.dumps(summary, indent=2))

print("")
print("=== RUNTIME FUSION SUMMARY ===")
for k, v in summary.items():
    print(f"{k}: {v}")
print("")
print(f"Wrote: {out_path}")
