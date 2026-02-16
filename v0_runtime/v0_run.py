
"""
GV Runtime V0 runner (single node demo)
"""

from gv_runtime import GVState, gv_step
import scenarios


def run(name, scenario_fn, threshold=1.0):
    print(f"\n--- Scenario: {name} ---")

    # GVState does NOT take threshold
    state = GVState(step=0, baseline=1.0, debt=0.0)

    history = []

    for value in scenario_fn():
        state = gv_step(state, value)
        history.append(state.debt)

        print(f"step={state.step} debt={state.debt:.4f}")

        if state.debt >= threshold:
            print("⚠️  Threshold breached")
            break

    return {
        "name": name,
        "final_debt": state.debt,
        "steps": state.step,
        "breached": state.debt >= threshold,
        "history": history,
    }


def main():
    results = []

    results.append(run("stable", scenarios.stable, threshold=1.0))
    results.append(run("volatile", scenarios.volatile, threshold=1.0))
    results.append(run("recovering", scenarios.recovering, threshold=1.0))

    print("\n=== Summary ===")
    for r in results:
        print(
            f"{r['name']}: debt={r['final_debt']:.4f} "
            f"steps={r['steps']} breached={r['breached']}"
        )


if __name__ == "__main__":
    main()
