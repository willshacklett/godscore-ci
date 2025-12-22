from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from gv_baseline.godscore import godscore, GVConfig


@dataclass(frozen=True)
class EvolutionResult:
    mean_scores: List[float]
    best_scores: List[float]
    best_cfgs: List[GVConfig]


def _make_candidate(rng: random.Random, n: int = 6):
    order = [rng.uniform(0.0, 5.0) for _ in range(n)]
    entropy = [rng.uniform(0.0, 5.0) for _ in range(n)]
    cfg = GVConfig(
        alpha=rng.uniform(0.5, 1.5),
        beta=rng.uniform(0.5, 1.5),
        gamma=rng.uniform(0.5, 2.0),
    )
    return (order, entropy, cfg)


def _mutate_cfg(rng: random.Random, cfg: GVConfig, sigma: float = 0.08) -> GVConfig:
    def clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, x))

    return GVConfig(
        alpha=clamp(cfg.alpha + rng.gauss(0.0, sigma), 0.1, 5.0),
        beta=clamp(cfg.beta + rng.gauss(0.0, sigma), 0.1, 5.0),
        gamma=clamp(cfg.gamma + rng.gauss(0.0, sigma), 0.1, 10.0),
    )


def _mutate_signals(rng: random.Random, xs, sigma: float = 0.15):
    return [max(0.0, x + rng.gauss(0.0, sigma)) for x in xs]


def _mutate_candidate(rng: random.Random, cand):
    order, entropy, cfg = cand
    return (
        _mutate_signals(rng, order),
        _mutate_signals(rng, entropy),
        _mutate_cfg(rng, cfg),
    )


def run_parameter_evolution(
    seed: int = 987654,
    pop_size: int = 350,
    generations: int = 14,
    survival_frac: float = 0.30,
) -> EvolutionResult:
    """
    Run a simple selection + mutation loop where each candidate carries its own
    GVConfig (alpha, beta, gamma). Returns per-generation histories.
    """
    rng = random.Random(seed)
    population = [_make_candidate(rng) for _ in range(pop_size)]

    mean_scores: List[float] = []
    best_scores: List[float] = []
    best_cfgs: List[GVConfig] = []

    for _ in range(generations):
        scored = sorted(
            ((godscore(o, e, cfg), (o, e, cfg)) for (o, e, cfg) in population),
            key=lambda t: t[0],
            reverse=True,
        )
        scores = [s for s, _ in scored]
        mean_scores.append(sum(scores) / len(scores))
        best_scores.append(scores[0])
        best_cfgs.append(scored[0][1][2])

        survivors = [c for _, c in scored[: int(pop_size * survival_frac)]]

        new_population = []
        while len(new_population) < pop_size:
            parent = rng.choice(survivors)
            child = _mutate_candidate(rng, parent)
            new_population.append(child)

        population = new_population

    return EvolutionResult(
        mean_scores=mean_scores,
        best_scores=best_scores,
        best_cfgs=best_cfgs,
    )
