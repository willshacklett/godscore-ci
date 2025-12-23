from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Literal, List, Optional
import random

from godscore_ci.envs import BridgeOrchardEnv

Action = Literal["REPAIR", "HARVEST", "BURN", "WAIT"]
State = Tuple[int, int, int]  # (t, b, o)


@dataclass
class QLearningConfig:
    episodes: int = 4000
    alpha: float = 0.25
    gamma: float = 0.98
    epsilon_start: float = 0.6
    epsilon_end: float = 0.05
    seed: int = 0


def _all_states(env: BridgeOrchardEnv) -> List[State]:
    states: List[State] = []
    for t in range(0, env.T + 1):
        for b in (0, 1):
            for o in (0, 1):
                states.append((t, b, o))
    return states


def _init_q(env: BridgeOrchardEnv) -> Dict[Tuple[State, Action], float]:
    Q: Dict[Tuple[State, Action], float] = {}
    for s in _all_states(env):
        for a in env.actions(s):
            Q[(s, a)] = 0.0
    return Q


def _greedy_action(env: BridgeOrchardEnv, Q: Dict[Tuple[State, Action], float], s: State) -> Action:
    best_a: Optional[Action] = None
    best_q: Optional[float] = None
    for a in env.actions(s):
        q = Q[(s, a)]
        if best_q is None or q > best_q:
            best_q = q
            best_a = a
    assert best_a is not None
    return best_a


def train_q_learning(
    env: BridgeOrchardEnv,
    lam: float,
    cfg: QLearningConfig = QLearningConfig(),
) -> Dict[Tuple[State, Action], float]:
    """
    Tabular Q-learning on deterministic finite-horizon env.
    Uses shaped reward: r' = r - lam * delta_omega
    """
    rnd = random.Random(cfg.seed)
    Q = _init_q(env)

    for ep in range(cfg.episodes):
        # Linear epsilon schedule
        frac = ep / max(1, (cfg.episodes - 1))
        eps = cfg.epsilon_start + frac * (cfg.epsilon_end - cfg.epsilon_start)

        s = env.start_state()
        while not env.is_terminal(s):
            # Epsilon-greedy
            if rnd.random() < eps:
                a = rnd.choice(list(env.actions(s)))
            else:
                a = _greedy_action(env, Q, s)

            r = env.reward(s, a) - lam * env.delta_omega(s, a)
            s2 = env.transition(s, a)

            # Next greedy value (off-policy)
            if env.is_terminal(s2):
                target = r
            else:
                a2 = _greedy_action(env, Q, s2)
                target = r + cfg.gamma * Q[(s2, a2)]

            Q[(s, a)] = (1.0 - cfg.alpha) * Q[(s, a)] + cfg.alpha * target
            s = s2

    return Q


def greedy_policy_from_q(env: BridgeOrchardEnv, Q: Dict[Tuple[State, Action], float]):
    """
    Returns a dict policy mapping state -> greedy action under Q.
    """
    pi = {}
    for s in _all_states(env):
        if env.is_terminal(s):
            continue
        pi[s] = _greedy_action(env, Q, s)
    return pi
