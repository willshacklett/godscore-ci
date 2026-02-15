from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass
class GVState:
    step: int = 0
    baseline: float = 0.0          # rolling trusted baseline (scalar for V0)
    baseline_alpha: float = 0.05    # how fast baseline adapts in stable mode
    debt: float = 0.0
    debt_decay: float = 0.98        # debt decays a bit each step
    drift_weight: float = 1.0
    risk_weight: float = 0.5
    threshold: float = 1.0

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def gv_step(state: GVState, signal: float, risk: float, update_baseline: bool) -> dict:
    """
    V0 simplification:
    - 'signal' is a scalar representing embedding distance / drift proxy.
    - 'risk' is a scalar representing boundary proximity (0..1).
    """
    # drift is distance from baseline
    drift = abs(signal - state.baseline)

    # accumulate debt (then decay)
    add = state.drift_weight * drift + state.risk_weight * risk
    state.debt = state.debt * state.debt_decay + add

    # optional baseline update (stable run)
    if update_baseline:
        state.baseline = (1 - state.baseline_alpha) * state.baseline + state.baseline_alpha * signal

    status = "OK" if state.debt < state.threshold else "TRIGGER"
    out = {
        "step": state.step,
        "signal": signal,
        "baseline": state.baseline,
        "drift": drift,
        "risk": risk,
        "debt": state.debt,
        "status": status,
    }
    state.step += 1
    return out
