import time
import json
import subprocess
from pathlib import Path

OUT = Path("outputs/runtime_signal")
OUT.mkdir(parents=True, exist_ok=True)

history_file = OUT / "runtime_history.jsonl"

def run_signal():
    subprocess.run(
        ["python", "scripts/runtime_signal.py", "examples/runtime_signal_input.csv"],
        check=True,
    )

    summary = json.loads(
        Path("outputs/runtime_signal/runtime_signal_input_summary.json").read_text()
    )

    return {
        "t_wall": int(time.time()),
        "score": summary.get("godscore_runtime"),
        "warned": summary.get("warned"),
        "first_warning_t": summary.get("first_warning_t"),
        "max_gv": summary.get("max_gv"),
        "max_persistence": summary.get("max_persistence"),
        "max_lag": summary.get("max_lag"),
    }

print("Starting runtime monitor loop...")

for _ in range(5):
    result = run_signal()
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")
    print("Logged:", result)
    time.sleep(2)

print(f"Wrote: {history_file}")
