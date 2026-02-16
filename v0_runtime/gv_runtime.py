from dataclasses import dataclass


@dataclass
class GVConfig:
    threshold: float = 1.0
    drift_rate: float = 0.05


@dataclass
class GVState:
    step: int = 0
    baseline: float = 0.0
    debt: float = 0.0


class GVRuntime:
    def __init__(self, cfg: GVConfig | None = None):
        self.cfg = cfg or GVConfig()
        self.state = GVState()

    def step(self, signal: float) -> dict:
        """
        Advance one step of the GV runtime.
        signal = entropy injection / drift input
        """

        # deterministic drift
        drift = self.cfg.drift_rate

        # update debt
        self.state.debt += drift + signal

        out = {
            "step": self.state.step,
            "drift": drift,
            "signal": signal,
            "debt": self.state.debt,
            "breached": self.breached(),
        }

        self.state.step += 1
        return out

    def breached(self) -> bool:
        return self.state.debt >= self.cfg.threshold

    def reset(self, baseline: float = 0.0) -> None:
        self.state = GVState(step=0, baseline=baseline, debt=0.0)
