"""
v0_run.py
GodScore CI – AutoScore v1 (GV Runtime Demo)

This runs simple scenarios and applies a threshold check
without passing threshold into GVState constructor.
"""

import json
from datetime import datetime

from scenarios import stable, drift, catastrophic
from gv_runtime import GVState


def run(name, scenario_func, threshold=1.0):
    """
    Execute a scenario and return a structured result.
    """

    # Run the scenario to get raw score components
    result = scenario_func()

    # Create GV state WITHOUT threshold argument
    state = GVState(
        loss=result["loss"],
        constraint_violation=result["constraint_violation"],
        recoverability=result["recoverability"],
    )

    godscore = state.score()

    return {
        "scenario": name,
        "godscore": godscore,
        "passed_threshold": godscore >= threshold,
        "timestamp": datetime.utcnow().isoformat()
    }


def main():
    threshold = 1.0
    outputs = []

    outputs.append(run("stable", stable, threshold))
    outputs.append(run("drift", drift, threshold))
    outputs.append(run("catastrophic", catastrophic, threshold))

    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
