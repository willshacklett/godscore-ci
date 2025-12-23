from __future__ import annotations

from dataclasses import dataclass

def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

@dataclass(frozen=True)
class GvWeights:
    robustness: float = 0.35
    coherence: float = 0.25
    adaptability: float = 0.20
    error_correction: float = 0.20

def gv_score(
    robustness: float,
    coherence: float,
    adaptability: float,
    error_correction: float,
    w: GvWeights = GvWeights(),
) -> float:
    """God Variable survivability proxy score in [0, 1]."""
    r = clamp01(robustness)
    c = clamp01(coherence)
    a = clamp01(adaptability)
    e = clamp01(error_correction)

    total_w = w.robustness + w.coherence + w.adaptability + w.error_correction
    if total_w <= 0:
        raise ValueError("Weights must sum to a positive value.")

    score = (w.robustness * r + w.coherence * c + w.adaptability * a + w.error_correction * e) / total_w
    return clamp01(score)
