from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class GVConfig:
    """
    Baseline configuration for the God Variable.

    alpha: weight of ordering forces
    beta: weight of entropic forces
    gamma: nonlinearity / sharpness
    """
    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 1.0


def _log1p_safe(x: float) -> float:
    if x < 0:
        raise ValueError("Signals must be non-negative.")
    return math.log1p(x)


def godscore(
    order_signals: Sequence[float],
    entropy_signals: Sequence[float],
    cfg: GVConfig = GVConfig(),
) -> float:
    """
    Returns a score in (0,1) representing dominance of order over entropy.

    score = sigmoid(
        gamma * (alpha * log(1 + sum(order)) - beta * log(1 + sum(entropy)))
    )
    """
    if not order_signals or not entropy_signals:
        raise ValueError("Signals cannot be empty.")

    if any(x < 0 for x in order_signals + entropy_signals):
        raise ValueError("Signals must be non-negative.")

    o = sum(order_signals)
    e = sum(entropy_signals)

    raw = cfg.gamma * (
        cfg.alpha * _log1p_safe(o)
        - cfg.beta * _log1p_safe(e)
    )

    # Numerically stable sigmoid
    if raw >= 0:
        z = math.exp(-raw)
        return 1 / (1 + z)
    else:
        z = math.exp(raw)
        return z / (1 + z)
