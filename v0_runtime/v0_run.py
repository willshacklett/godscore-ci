"""
GV Runtime V0 runner
Single-node deterministic drift + optional abrupt breach scenario
"""

from gv_runtime import GVState, gv_step
import scenarios


def run(name, scenario_fn, threshold=1.0, steps=25):
    """
    Execute a scenario for N steps and return summary output.
    """
    state = GVState(step=0, baseline=0.0, debt=0.0)

    history = []

    for _ in range(steps):
        delta = scenario_fn(state)
        gv_step(state, delta)

        breached = state.debt >= threshold

        history.append({
            "step": state.step,
            "delta": delta,
            "debt": state.debt,
            "breached": breached,
        })

        if breached:
            break

    return {
        "name": name,
        "final_step": state.step,
        "final_debt": state.debt,
        "breached": state.debt >= threshold,
        "history": history,
    }


def main():
    outputs = []

    outputs.append(run("stable", scenarios.stable))
    outputs.append(run("linear_drift", scenarios.linear_drift))
    outputs.append(run("abrupt_spike", scenarios.abrupt_spike))

    for result in outputs:
        print("\n==============================")
        print(f"Scenario: {result['name']}")
        print(f"Final Step: {result['final_step']}")
        print(f"Final Debt: {result['final_debt']:.4f}")
        print(f"Breach: {result['breached']}")
        print("==============================")


if __name__ == "__main__":
    main()
