# gv_runtime.py
# GV Runtime V0 (single-node)
# - Drift = |signal - baseline|
# - Risk  = boundary proximity (0..1)
# - Debt accumulates with decay
# - Optional baseline learning ONLY during stable runs

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class GVConfig:
    # Baseline update rate (only used when update_baseline=True)
    baseline_alpha: float = 0.05

    # Debt decay (0.0 = no decay, 1.0 = full reset each step)
    # Typical: 0.01–0.05
    debt_decay: float = 0.02

    # Weights
    drift_weight: float = 1.0
    risk_weight: float = 0.5

    # Trigger threshold
    threshold: float = 1.0


@dataclass
class GVState:
    step: int = 0
    baseline: float = 0.0
    debt: float = 0.0


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class GVRuntime:
    """
    Minimal V0 runtime.

    Inputs per step:
      - signal: scalar drift proxy (e.g., embedding distance-like value)
      - risk:   scalar boundary proximity in [0, 1]
      - update_baseline: if True, baseline learns slowly from signal (stable only)

    Output:
      dict with step metrics + status
    """

    def __init__(self, config: GVConfig | None = None, state: GVState | None = None):
        self.cfg = config or GVConfig()
        self.state = state or GVState()

        # sanitize
        self.cfg.baseline_alpha = clamp(self.cfg.baseline_alpha, 0.0, 1.0)
        self.cfg.debt_decay = clamp(self.cfg.debt_decay, 0.0, 1.0)
        self.cfg.threshold = max(0.0, self.cfg.threshold)

    def step(self, signal: float, risk: float = 0.0, update_baseline: bool = False) -> dict:
        s = self.state
        c = self.cfg

        # keep risk sane
        risk = clamp(risk, 0.0, 1.0)

        # 1) Drift = distance from baseline
        drift = abs(signal - s.baseline)

        # 2) Debt update: decay old debt, add new instability
        # decay: debt *= (1 - decay)
        s.debt *= (1.0 - c.debt_decay)
        s.debt += (c.drift_weight * drift) + (c.risk_weight * risk)

        # 3) Optional baseline update (stable only)
        if update_baseline:
            s.baseline = (1.0 - c.baseline_alpha) * s.baseline + c.baseline_alpha * signal

        # 4) Status
        status = "OK" if s.debt < c.threshold else "TRIGGER"

        out = {
            "step": s.step,
            "signal": float(signal),
            "baseline": float(s.baseline),
            "drift": float(drift),
            "risk": float(risk),
            "debt": float(s.debt),
            "threshold": float(c.threshold),
            "status": status,
        }

        s.step += 1
        return out

    def breached(self) -> bool:
        return self.state.debt >= self.cfg.threshold

    def reset(self, baseline: float = 0.0) -> None:
        self.state = GVState(step=0, baseline=baseline, debt=0.0)
