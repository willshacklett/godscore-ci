import scenarios
from gv_runtime import GVState, gv_step


def run(name, signal_series, decay=0.99):
    state = GVState(step=0, baseline=signal_series[0], debt=0.0)
    debt_curve = []

    for s in signal_series:
        state = gv_step(state, s, decay=decay)
        debt_curve.append(state.debt)

    return {
        "scenario": name,
        "final_debt": state.debt,
        "max_debt": max(debt_curve),
    }


def main():
    out = []

    out.append(run("stable", scenarios.stable()))
    out.append(run("gradual", scenarios.gradual()))
    out.append(run("abrupt", scenarios.abrupt()))

    for r in out:
        print(r)


if __name__ == "__main__":
    main()
