"""
GV Runtime V0 Runner
Single-node deterministic scenario runner
"""

from gv_runtime import GVState, GVRuntime
import scenarios


def run(name: str, scenario_fn, threshold: float = 1.0):
    print(f"\n--- Running scenario: {name} ---")

    # Initial state
    state = GVState(step=0, baseline=0.0, debt=0.0)

    # Runtime wrapper holds threshold
    runtime = GVRuntime(state=state, threshold=threshold)

    # Execute scenario steps
    for delta in scenario_fn():
        runtime.step(delta)

        print(
            f"step={runtime.state.step} "
            f"debt={runtime.state.debt:.4f}"
        )

        if runtime.breached():
            print("⚠️  Threshold breached.")
            break

    return {
        "scenario": name,
        "final_step": runtime.state.step,
        "final_debt": runtime.state.debt,
        "breached": runtime.breached(),
    }


def main():
    results = []

    results.append(run("stable", scenarios.stable, threshold=1.0))
    results.append(run("drift", scenarios.drift, threshold=1.0))
    results.append(run("shock", scenarios.shock, threshold=1.0))

    print("\n=== Summary ===")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
