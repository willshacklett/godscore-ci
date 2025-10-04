
"""
GodScore Moral Field Module
---------------------------
Encodes the "Objective Good" moral field potential Φ_G and decision helpers.
Pure standard library. No external deps.
"""
from dataclasses import dataclass
from typing import Dict, Any, Iterable, Tuple

@dataclass
class Config:
    kappa_G: float
    weights: Dict[str, float]
    thresholds: Dict[str, float]

DEFAULT_WEIGHTS = {"good":1.0, "evil":1.0, "hope":1.0, "fear":1.0, "coherence":1.0, "harm":1.0}
DEFAULT_THRESHOLDS = {"nonmaleficence":0.5, "autonomy":0.5, "justice":0.5, "truthfulness":0.6}

DEFAULT_CONFIG = Config(
    kappa_G=1.0,
    weights=DEFAULT_WEIGHTS,
    thresholds=DEFAULT_THRESHOLDS
)

def phi_G(scores: Dict[str, float], w: Dict[str, float]) -> float:
    """
    Φ_G = w_g*Good - w_e*Evil + w_h*Hope - w_f*Fear + w_c*Coherence - w_hm*Harm
    All inputs are expected in [0,1]. Missing keys default to 0.
    """
    return (
        w.get("good",1.0)*scores.get("good",0.0)
        - w.get("evil",1.0)*scores.get("evil",0.0)
        + w.get("hope",1.0)*scores.get("hope",0.0)
        - w.get("fear",1.0)*scores.get("fear",0.0)
        + w.get("coherence",1.0)*scores.get("coherence",0.0)
        - w.get("harm",1.0)*scores.get("harm",0.0)
    )

def admissible(constraints: Dict[str, float], thresholds: Dict[str, float]) -> bool:
    """
    Checks hard ethical constraints (rights as invariants).
    Each constraint must be >= corresponding threshold.
    Unknown constraints are ignored.
    """
    for k, tau in thresholds.items():
        v = constraints.get(k, 0.0)
        if v < tau:
            return False
    return True

def value(env_reward: float, scores: Dict[str, float], config: Config = DEFAULT_CONFIG) -> float:
    """Combined planner objective for a single action."""
    return env_reward + config.kappa_G * phi_G(scores, config.weights)

def choose_action(
    state: Any,
    candidates: Iterable[Any],
    model_eval_fn,
    config: Config = DEFAULT_CONFIG
) -> Tuple[Any, float]:
    """Pick the admissible action with maximal env_reward + κ_G*Φ_G.
    - model_eval_fn(state, a) must return a dict with keys:
      { "env_reward": float,
        "scores": {good, evil, hope, fear, coherence, harm},
        "constraints": {nonmaleficence, autonomy, justice, truthfulness}
      }
    Returns (best_action, best_value). If none admissible, returns (None, float('-inf')).
    """
    best, best_val = None, float("-inf")
    for a in candidates:
        pred = model_eval_fn(state, a)
        scores = pred.get("scores", {})
        constraints = pred.get("constraints", {})
        if not admissible(constraints, config.thresholds):
            continue
        v = value(pred.get("env_reward", 0.0), scores, config)
        if v > best_val:
            best, best_val = a, v
    return best, best_val
