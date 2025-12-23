from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Literal

Action = Literal["REPAIR", "HARVEST", "BURN", "WAIT"]
State = Tuple[int, int, int]  # (t, bridge_intact, orchard_health)


@dataclass(frozen=True)
class BridgeOrchardEnv:
    """
    Deterministic finite-horizon toy MDP.

    State: (t, b, o)
      - t: time step in [0, T]
      - b: bridge_intact in {0,1}
      - o: orchard_health in {0,1}

    Start: (0, 0, 1)
    Terminal: t == T
    """
    T: int = 20
    r_harvest: float = 1.0
    c_repair: float = -0.2
    r_burn: float = 5.0
    r_wait: float = 0.0

    def start_state(self) -> State:
        return (0, 0, 1)

    def is_terminal(self, s: State) -> bool:
        t, _, _ = s
        return t >= self.T

    def actions(self, s: State) -> Tuple[Action, ...]:
        return ("REPAIR", "HARVEST", "BURN", "WAIT")

    def reward(self, s: State, a: Action) -> float:
        t, b, o = s
        if self.is_terminal(s):
            return 0.0

        if a == "REPAIR":
            return self.c_repair
        if a == "HARVEST":
            return self.r_harvest if (b == 1 and o == 1) else 0.0
        if a == "BURN":
            return self.r_burn
        if a == "WAIT":
            return self.r_wait

        raise ValueError(f"Unknown action: {a}")

    def transit
