import numpy as np

class GVState:
    def __init__(self, decay=0.95, threshold=10.0):
        self.debt = 0.0
        self.decay = decay
        self.threshold = threshold
        self.history = []

    def record(self):
        self.history.append(self.debt)

def gv_step(state: GVState, signal: float):
    """
    Single GV update step.
    signal: external instability input
    """
    # Apply decay to existing debt
    state.debt *= state.decay

    # Add new instability
    state.debt += signal

    # Record history
    state.record()

    # Check violation
    violated = state.debt >= state.threshold

    return violated
