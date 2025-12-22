import random

from gv_baseline.godscore import godscore


def _jitter_nonnegative(values, eps, rng):
    """
    Add small uniform noise in [-eps, +eps] and clamp at 0.
    """
    out = []
    for v in values:
        v2 = v + rng.uniform(-eps, eps)
        out.append(max(0.0, v2))
    return out


def test_perturbation_stability_small_noise():
    """
    If we add very small noise to inputs, the score should not jump wildly.
    This is a robustness / stability check.
    """
    rng = random.Random(1337)

    base_order = [1.0, 2.0, 3.0, 4.0]
    base_entropy = [1.5, 1.0, 2.5, 1.0]

    s0 = godscore(base_order, base_entropy)

    eps = 1e-3  # tiny perturbation
    max_delta = 2e-3  # generous bound for the baseline sigmoid+log1p form

    # multiple trials to avoid a fluke
    for _ in range(200):
        o2 = _jitter_nonnegative(base_order, eps, rng)
        e2 = _jitter_nonnegative(base_entropy, eps, rng)
        s1 = godscore(o2, e2)

        assert abs(s1 - s0) <= max_delta


def test_perturbation_does_not_break_monotonic_trend():
    """
    Even with tiny noise, higher-order inputs should tend to score higher
    than lower-order inputs (with identical entropy).
    """
    rng = random.Random(2025)

    low_order = [1.0, 1.0, 1.0]
    high_order = [2.0, 2.0, 2.0]
    entropy = [1.0, 1.0, 1.0]

    eps = 1e-3

    # sample a bunch of noisy comparisons
    wins = 0
    trials = 200
    for _ in range(trials):
        lo = _jitter_nonnegative(low_order, eps, rng)
        hi = _jitter_nonnegative(high_order, eps, rng)
        en = _jitter_nonnegative(entropy, eps, rng)

        if godscore(hi, en) > godscore(lo, en):
            wins += 1

    # should win the overwhelming majority of the time
    assert wins >= int(0.95 * trials)
