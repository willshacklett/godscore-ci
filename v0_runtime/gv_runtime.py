from dataclasses import dataclass


@dataclass
class GVState:
    step: int = 0
    baseline: float = 0.0
    debt: float = 0.0


def gv_step(state: GVState, signal: float, decay: float = 0.99) -> GVState:
    """
    Single GV update step.
    Debt increases as signal diverges from baseline.
    """

    drift = signal - state.baseline

    # decay old debt
    state.debt *= decay

    # accumulate new divergence
    state.debt += abs(drift)

    state.step += 1

    return state
