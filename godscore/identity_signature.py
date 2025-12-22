from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class IdentitySignature:
    """
    Experimental identity signature for a multivariate dynamical system.

    Notes:
    - This is descriptive, not metaphysical.
    - Values are proxy metrics intended for comparative experiments.
    """
    integration: float   # I_int: cross-component coupling proxy
    recurrence: float    # R: stability of structure across time windows
    feedback: float      # C: directed lag influence proxy
    decay: float         # D: sensitivity to perturbation (higher = more fragile)

    def as_vector(self) -> np.ndarray:
        return np.array([self.integration, self.recurrence, self.feedback, self.decay], dtype=float)

    def continuity_to(self, other: "IdentitySignature") -> float:
        """
        Continuity in [0, 1] where 1 means identical signatures.
        Uses normalized distance between signature vectors.
        """
        a = self.as_vector()
        b = other.as_vector()
        denom = (np.linalg.norm(a) + np.linalg.norm(b) + 1e-12)
        dist = np.linalg.norm(a - b) / denom
        return float(np.clip(1.0 - dist, 0.0, 1.0))


def compute_identity_signature(
    X: np.ndarray,
    *,
    window: int =

