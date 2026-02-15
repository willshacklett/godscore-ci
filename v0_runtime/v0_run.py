import os
import pandas as pd
import matplotlib.pyplot as plt

from gv_runtime import GVState, gv_step
import scenarios

def run(name: str, gen, threshold=1.0, outdir="out"):
    state = GVState(threshold=threshold)
    rows = []
    for signal, risk, update_baseline in gen:
        rows.append(gv_step(state, signal=signal, risk=risk, update_baseline=update_baseline))

    df = pd.DataFrame(rows)
    os.makedirs(outdir, exist_ok=True)
    csv_path = os.path.join(outdir, f"{name}.csv")
    df.to_csv(csv_path, index=False)

    # Plot debt curve
    plt.figure()
    plt.plot(df["step"], df["debt"])
    plt.axhline(threshold)
    plt.title(f"V0 Debt Curve – {name}")
    plt.xlabel("step")
    plt.ylabel("debt")
    png_path = os.path.join(outdir, f"{name}.png")
    plt.savefig(png_path, dpi=180, bbox_inches="tight")
    plt.close()

    # Basic metrics
    triggers = (df["status"] == "TRIGGER").sum()
    first_trigger = df.index[df["status"] == "TRIGGER"]
    first_trigger_step = int(df.loc[first_trigger[0], "step"]) if len(first_trigger) else None

    return {
        "name": name,
        "csv": csv_path,
        "png": png_path,
        "triggers": int(triggers),
        "first_trigger_step": first_trigger_step,
        "final_debt": float(df["debt"].iloc[-1]),
    }

def main():
    out = []
    out.append(run("stable", scenarios.stable(), threshold=1.0))
    out.append(run("gradual_drift", scenarios.gradual_drift(), threshold=1.0))
    out.append(run("abrupt_violation", scenarios.abrupt_violation(), threshold=1.0))

    print("\nV0 summary:")
    for r in out:
        print(r)

if __name__ == "__main__":
    main()
