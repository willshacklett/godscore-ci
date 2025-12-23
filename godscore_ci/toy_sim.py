from __future__ import annotations

from dataclasses import dataclass
import random

from .gv_score import gv_score


@dataclass
class ToySystem:
    """
    Minimal survivability toy system.

    This is not physics.
    It is a falsifiable demonstration of selection under perturbation.
    """
    redundancy: float
    repair_rate: float
    coherence_penalty: float
    adaptability: float

    damage: float = 0.0
    shock_multiplier: float = 1.0

    def step(self, rng: random.Random, shock_strength: float) -> None:
        shock = shock_strength * self.shock_multiplier

        # redundancy buffers incoming shock
        effective = shock * (1.0 - 0.6 * self.redundancy)
        self.damage += max(0.0, effective)

        # error correction repairs damage
        self.damage = max(0.0, self.damage - self.repair_rate * 0.8)

        # adaptability slowly reduces future shocks
        if rng.random() < self.adaptability * 0.15:
            self.shock_multiplier = max(0.4, self.shock_multiplier * 0.97)

    def alive(self) -> bool:
        return self.damage < 10.0

    def score(self) -> float:
        robustness = self.redundancy
        error_correction = self.repair_rate
        coherence = max(0.0, 1.0 - self.coherence_penalty * min(1.0, self.damage / 10.0))
        adaptability = self.adaptability

        return gv_score(
            robustness=robustness,
            coherence=coherence,
            adaptability=adaptability,
            error_correction=error_correction,
        )


def run_trial(
    system: ToySystem,
    *,
    seed: int,
    max_steps: int = 400,
    base_shock: float = 0.35,
    shock_jitter: float = 0.25,
) -> int:
    rng = random.Random(seed)
    steps = 0

    while steps < max_steps and system.alive():
        shock = base_shock + rng.random() * shock_jitter
        system.step(rng, shock_strength=shock)
        steps += 1

    return steps
