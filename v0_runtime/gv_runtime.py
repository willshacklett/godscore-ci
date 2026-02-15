import numpy as np


class GVState:
    """
    Minimal single-node GV runtime state.
    Tracks debt accumulation over time.
    """

    def __init__(self, decay=0.01):
        self.debt = 0.0
        self.decay = decay
        self.history = []

    def update(self, signal):
        """
        Update debt based on incoming instability signal.
        signal: float (e.g., entropy / drift magnitude)
        """
        # Exponential decay on previous debt
        self.debt *= (1 - self.decay)

        # Accumulate new signal
        self.debt += signal

        # Store history
        self.history.append(self.debt)

        return self.debt


def gv_step(state: GVState, signal: float):
    """
    One GV runtime step.
    Returns updated debt value.
    """
    return state.update(signal)
