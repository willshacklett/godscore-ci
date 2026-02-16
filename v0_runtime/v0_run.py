"""
V0 Runtime Runner
Runs simple scenarios through GVState and prints results.

This is a minimal, local test harness for the God Variable runtime.
"""

from gv_runtime import GVState
from scenarios import SCENARIOS


def run(label: str, scenario: dict):
    """
    Run a single scenario through GVState.
    """
    state = GVState()

    # Apply scenario inputs
    for key, value in scenario.items():
        setattr(state, key, value)

    score = state.compute_gv()

    return {
        "label": label,
        "gv_score": score,
        "state": state.__dict__,
    }


def main():
    results = []

    for label, scenario in SCENARIOS.items():
        results.append(run(label, scenario))

    print("\n=== GV V0 Runtime Results ===\n")

    for result in results:
        print(f"Scenario: {result['label']}")
        print(f"GV Score: {result['gv_score']:.4f}")
        print("-" * 40)


if __name__ == "__main__":
    main()
