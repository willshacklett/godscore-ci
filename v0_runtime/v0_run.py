import json
from datetime import datetime

from gv_runtime import GVState
import scenarios


def run(label, scenario_fn):
    """
    Run a single scenario and return result dictionary.
    """
    state = GVState()  # <-- NO threshold passed here

    # Apply scenario mutations
    scenario_fn(state)

    result = {
        "label": label,
        "timestamp": datetime.utcnow().isoformat(),
        "dgv": state.dgv,
        "recoverability": state.recoverability,
        "stability": state.stability,
        "score": state.score()
    }

    return result


def main():
    results = []

    results.append(run("stable", scenarios.stable))
    results.append(run("drift", scenarios.drift))
    results.append(run("collapse", scenarios.collapse))

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
