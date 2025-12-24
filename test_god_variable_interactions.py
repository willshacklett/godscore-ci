# test_god_variable_interactions.py
import math


# Reference implementation used for tests.
# This file tests aggregation invariants (order, monotonicity, bounds).
# It is intentionally independent of the GodVariable penalty model.


def god_variable(
    components: dict[str, float],
    weights: dict[str, float] | None = None,
    bounds: tuple[float, float] = (0.0, 1.0),
) -> float:
    """
    Aggregate multiple components into a scalar value:
    - clamps each component into [lo, hi]
    - applies (normalized) weights
    - returns a weighted average
    """
    lo, hi = bounds
    if lo >= hi:
        raise ValueError("bounds must satisfy lo < hi")

    # Clamp and normalize
    clamped = {}
    for k, v in components.items():
        vv = min(max(v, lo), hi)
        clamped[k] = (vv - lo) / (hi - lo)

    if not components:
        return lo

    if weights is None:
        weights = {k: 1.0 for k in components}
    else:
        weights = {k: float(weights.get(k, 0.0)) for k in components}

    total_w = sum(max(w, 0.0) for w in weights.values())
    if total_w <= 0:
        return (lo + hi) / 2.0

    s = 0.0
    for k, v in clamped.items():
        w = max(weights.get(k, 0.0), 0.0)
        s += w * v

    mixed = s / total_w
    return lo + mixed * (hi - lo)


def approx(a, b, tol=1e-9):
    return abs(a - b) <= tol


def test_commutativity():
    a = {"x": 0.2, "y": 0.9, "z": 0.5}
    b = {"z": 0.5, "x": 0.2, "y": 0.9}
    assert approx(god_variable(a), god_variable(b))


def test_associativity_approx():
    A = {"a": 0.2, "b": 0.8}
    B = {"c": 0.4, "d": 0.6}

    r_all = god_variable({**A, **B})
    r_A = god_variable(A)
    r_B = god_variable(B)
    r_two = god_variable({"A": r_A, "B": r_B})

    assert approx(r_all, r_two)


def test_monotonicity():
    base = {"a": 0.2, "b": 0.3}
    higher = {"a": 0.2, "b": 0.9}
    assert god_variable(higher) >= god_variable(base)


def test_weighting_effect():
    comps = {"a": 0.2, "b": 0.9}
    r_equal = god_variable(comps, weights={"a": 1, "b": 1})
    r_b_heavy = god_variable(comps, weights={"a": 1, "b": 5})
    assert r_b_heavy > r_equal


def test_bounds_respected():
    comps = {"a": -100, "b": 1000}
    r = god_variable(comps, bounds=(0.0, 1.0))
    assert 0.0 <= r <= 1.0
