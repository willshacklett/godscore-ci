import os
import csv
from datetime import datetime


# ---------------------------
# Simple GodScore Runtime v0
# ---------------------------

def compute_godscore(gv: float) -> float:
    """
    GodScore = 1 - GV
    Lower GV = better system recoverability
    """
    return round(1.0 - gv, 4)


def run_scenario(name: str, gv: float, threshold: float = 0.80):
    score = compute_godscore(gv)
    passed = score >= threshold

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "scenario": name,
        "gv": gv,
        "godscore": score,
        "threshold": threshold,
        "passed": passed
    }


def write_csv(results, output_path="v0_output.csv"):
    file_exists = os.path.isfile(output_path)

    with open(output_path, mode="a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "scenario", "gv", "godscore", "threshold", "passed"]
        )

        if not file_exists:
            writer.writeheader()

        for row in results:
            writer.writerow(row)


def main():
    print("Running GodScore v0 runtime...")

    scenarios = [
        run_scenario("stable", gv=0.10),
        run_scenario("minor_regression", gv=0.25),
        run_scenario("major_regression", gv=0.60),
    ]

    write_csv(scenarios)

    for s in scenarios:
        print(
            f"[{s['scenario']}] "
            f"GV={s['gv']} "
            f"GodScore={s['godscore']} "
            f"Passed={s['passed']}"
        )

    print("Done.")


if __name__ == "__main__":
    main()
