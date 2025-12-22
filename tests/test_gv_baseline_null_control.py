import random
import statistics


def _make_candidate(rng, n=6):
    # same structure as selection tests: nonnegative signals
    order = [rng.uniform(0.0, 5.0) for _ in range(n)]
    entropy = [rng.uniform(0.0, 5.0) for _ in range(n)]
    return (order, entropy)


def _mutate_candidate(rng, cand, sigma=0.15):
    order, entropy = cand
    order2 = [max(0.0, x + rng.gauss(0.0, sigma)) for x in order]
    entropy2 = [max(0.0, x + rng.gauss(0.0, sigma)) for x in entropy]
    return (order2, entropy2)


def test_null_control_random_score_does_not_improve_trend():
    """
    Control group: selection on a RANDOM score should not reliably improve the mean
    across generations. This helps demonstrate the real 'godscore' improvement
    isn't a trivial artifact of the loop.
    """
    rng = random.Random(123456)

    pop_size = 400
    generations = 12
    survival_frac = 0.35

    population = [_make_candidate(rng) for _ in range(pop_size)]

    means = []
    for _ in range(generations):
        # Random "fitness" independent of candidate
        scored = sorted(((rng.random(), c) for c in population), key=lambda t: t[0], reverse=True)
        scores = [s for s, _ in scored]
        means.append(statistics.mean(scores))

        survivors = [c for _, c in scored[: int(pop_size * survival_frac)]]

        new_population = []
        while len(new_population) < pop_size:
            parent = rng.choice(survivors)
            child = _mutate_candidate(rng, parent)
            new_population.append(child)

        population = new_population

    # Random mean should hover near 0.5; it should not jump by a large margin
    assert abs(means[-1] - means[0]) < 0.10

    # Trend should NOT be strongly upward: require less than 70% upward steps
    upward_steps = sum(1 for i in range(1, len(means)) if means[i] > means[i - 1])
    assert upward_steps <= int(0.70 * (len(means) - 1))
