from __future__ import annotations

from typing import Dict, Tuple, Optional, Literal

from godscore_ci.envs import BridgeOrchardEnv

Action = Literal["REPAIR", "HARVEST", "BURN", "WAIT"]
State = Tuple[int, int, int]  # (t, b, o)


def backward_value_iteration(
    env: BridgeOrchardEnv,
    gamma: float = 0.98,
    lam: float = 0.0,
) -> Tuple[Dict[State, float], Dict[State, Action]]:
    """
    Finite-horizon backward induction with optional Gv penalty.

    Utility:
        u(s,a) = reward(s,a) - lam * delta_omega(s,a)

    Deterministic and exact.
    """
    V: Dict[State, float] = {}
    pi: Dict[State, Action] = {}

    # Terminal values
    for b in (0, 1):
        for o in (0, 1):
            V[(env.T, b, o)] = 0.0

    # Backward induction
    for t in range(env.T - 1, -1, -1):
        for b in (0, 1):
            for o in (0, 1):
                s: State = (t, b, o)

                best_value: Optional[float] = None
                best_action: Optional[Action] = None

                for a in env.actions(s):
                    r = env.reward(s, a)
                    penalty = lam * env.delta_omega(s, a)
                    u = r - penalty

                    s_next = env.transition(s, a)
                    q = u + gamma * V[s_next]

                    if best_value is None or q > best_value:
                        best_value = q
                        best_action = a

                V[s] = best_value
                pi[s] = best_action

    return V, pi
