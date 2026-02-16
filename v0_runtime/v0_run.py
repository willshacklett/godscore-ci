from gv_runtime import GVState
import scenarios


def run(name, scenario_func):
    """
    Runs a scenario and returns structured result.
    """

    state = GVState()  # <-- NO threshold argument

    # Apply scenario
    scenario_func(state)

    # Compute score
    score = state.score()

    return {
        "scenario": name,
        "score": score,
        "recoverability": state.recoverability,
        "constraint_pressure": state.constraint_pressure,
    }


def main():
    results = []

    results.append(run("stable", scenarios.stable))
    results.append(run("drift", scenarios.drift))
    results.append(run("collapse", scenarios.collapse))

    print("\n=== GV v0 Runtime Results ===\n")

    for r in results:
        print(f"Scenario: {r['scenario']}")
        print(f"  Score: {r['score']}")
        print(f"  Recoverability: {r['recoverability']}")
        print(f"  Constraint Pressure: {r['constraint_pressure']}")
        print("")


if __name__ == "__main__":
    main()
