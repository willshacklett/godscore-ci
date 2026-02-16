"""
v0_run.py

Simple runtime demo for GV (God Variable).
Runs a few synthetic scenarios and prints resulting state.
"""

from gv_runtime import GVState


def run(name: str, scenario_fn):
    """
    Run a single scenario and return summary.
    """
    state = GVState()  # <-- no threshold passed here

    scenario_fn(state)

    return {
        "scenario": name,
        "health": round(state.health, 3),
        "constraint_debt": round(state.constraint_debt, 3),
        "collapsed": state.collapsed,
    }


# -------------------------
# SCENARIOS
# -------------------------

def stable(state: GVState):
    """
    Healthy system — low constraint pressure.
    """
    for _ in range(10):
        state.update(
            pressure=0.2,
            recoverability=0.9,
            threshold=1.0
        )


def degrading(state: GVState):
    """
    System slowly degrading.
    """
    for _ in range(10):
        state.update(
            pressure=0.6,
            recoverability=0.4,
            threshold=1.0
        )


def collapse(state: GVState):
    """
    High pressure system that collapses.
    """
    for _ in range(10):
        state.update(
            pressure=1.2,
            recoverability=0.1,
            threshold=1.0
        )


# -------------------------
# MAIN
# -------------------------

def main():
    results = []

    results.append(run("stable", stable))
    results.append(run("degrading", degrading))
    results.append(run("collapse", collapse))

    print("\nGV Runtime Demo Results\n" + "-" * 30)

    for r in results:
        print(r)


if __name__ == "__main__":
    main()
