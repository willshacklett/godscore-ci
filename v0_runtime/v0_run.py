"""
v0_run.py

Minimal V0 runner for GV Runtime.
Runs simple deterministic + stochastic scenarios
and reports breach behavior.
"""

from gv_runtime import GVRuntime, GVConfig
import scenarios


def run(name, scenario_fn, threshold=1.0):
    """
    Execute a scenario against the GV runtime.
    """
    runtime = GVRuntime(GVConfig(threshold=threshold))
    history = []

    for signal in scenario_fn():
        result = runtime.step(signal)
        history.append(result)

        if result["breached"]:
            break

    return {
        "name": name,
        "steps": len(history),
        "breached": runtime.breached(),
        "final_debt": runtime.state.debt,
    }


def main():
    results = []

    results.append(run("stable", scenarios.stable, threshold=1.0))
    results.append(run("drift", scenarios.drift, threshold=1.0))
    results.append(run("spike", scenarios.spike, threshold=1.0))

    print("\n=== GV Runtime V0 Results ===\n")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
