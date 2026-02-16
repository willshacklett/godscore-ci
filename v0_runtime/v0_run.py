import json
from datetime import datetime
from scenarios import SCENARIOS
from gv_runtime import GVState


def run(label: str, scenario: dict, threshold: float = 1.0):
    """
    Runs a single GV scenario and returns structured result.
    """

    # IMPORTANT: Do NOT pass threshold into GVState constructor
    state = GVState()

    # Apply scenario inputs
    state.constraint_load = scenario.get("constraint_load", 0.0)
    state.recoverability = scenario.get("recoverability", 1.0)
    state.entropy = scenario.get("entropy", 0.0)

    # Compute score
    score = state.compute_gv()

    return {
        "label": label,
        "timestamp": datetime.utcnow().isoformat(),
        "constraint_load": state.constraint_load,
        "recoverability": state.recoverability,
        "entropy": state.entropy,
        "gv_score": score,
        "threshold": threshold,
        "passed": score >= threshold,
    }


def main():
    results = []

    for label, scenario in SCENARIOS.items():
        results.append(run(label, scenario, threshold=1.0))

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
