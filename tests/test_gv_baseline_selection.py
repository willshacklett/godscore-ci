import random
import statistics

from gv_baseline.godscore import godscore


def _make_candidate(rng, n_order=6, n_entropy=6):
    # Positive signals (order and entropy pressures)
    order = [rng.uniform(0.0, 5.0) for _ in range(n_order)]
    entropy = [rng.uniform(0.0, 5.0) for _ in range(n_entropy)]
    return (order, entropy)


def _mutate_candidate(rng, candidate, sigma=0.15):
    # Small Gaussian mutation, clamped at 0 to preserve non-negativity
    order, entropy = candidate
    order2 = [max(0.0, x + rng.gauss(0.0, sigma)) for x in order]
    entropy2 = [max(0.0, x + rng.gauss(0.0, sigma)) for x in entropy]
    return (order2, entropy2)


def _score(candidate):
    order, entropy = candidate
    return godscore(order, entropy)


def test_selection_increases_mean_godscore_over_generations():
    rng = random.Random(424242)

    pop_size = 400
    generations = 12
    survival_frac = 0.35  # keep top 35%

    # Initialize population
    population = [_make_candidate(rng) for _ in range(pop_size)]

    means = []
    for _ in range(generations):
        scored = sorted((( _score(c), c) for c in population), key=lambda t: t[0], reverse=True)
        scores = [s for s, _ in scored]
        means.append(statistics.mean(scores))

        # Select survivors (top fraction)
        survivors = [c for _, c in scored[: int(pop_size * survival_frac)]]

        # Reproduce with mutation to refill population
        new_population = []
        while len(new_population) < pop_size:
            parent = rng.choice(survivors)
            child = _mutate_candidate(rng, parent)
            new_population.append(child)

        population = new_population

    #
