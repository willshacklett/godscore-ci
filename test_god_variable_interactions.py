# test_god_variable_interactions.py
import math

# Reference implementation used for tests.
# You can later replace this with: from your_module import god_variable
def god_variable(components: dict[str, float],
                 weights: dict[str, float] | None = None,
                 bounds: tuple[float, float] = (0.0, 1.0)) -> float:
    """
    Aggregate multiple components into the God Variable:
    - clamps each component into [lo, hi]
    - applies (normalized) weights
    - returns a weighted average
    """
    lo, hi = bounds
    if lo >= hi:
        raise ValueError("bounds must satisfy lo < hi")

    # Clamp and re-scale to [0, 1] internally for stable math, then map back
    clamped = {}
    for k, v in components.items():
        vv = min(max(v, lo), hi)
        # normalize to 0..1 for mixing, then map back to [lo, hi] at the end
        clamped[k] = (vv - lo) / (hi - lo)

    # If no weights, use equal weights
    if not components:
        return lo  # empty -> lowest value by convention
    if weights is None:
        weights = {k: 1.0 for k in components}
    else:
        # ensure every component has a weight; default to 0 for missing
        weights = {k: float(weights.get(k, 0.0)) for k in components}

    total_w = sum(max(w, 0.0) for w in weights.values())
    if total_w <= 0:
        # if all weights are zero, define neutral result (midpoint)
        return (lo + hi) / 2.0

    # Weighted arithmetic mean in normalized space
    s = 0.0
    for k, v in clamped.items():
        w = max(weights.get(k, 0.0), 0.0)
        s += w * v
    mixed_norm = s / total_w

    # Map back to original bounds
    return lo + mixed_norm * (hi - lo)


def approx(a, b, tol=1e-9):
    return abs(a - b) <= tol


# CLAIM: GLB-1 (Global coherence — result must not depend on component order)
def test_commutativity():
    comps1 = {"a": 0.2, "b": 0.9, "c": 0.5}
    comps2 = {"b": 0.9, "c": 0.5, "a": 0.2}
    r1 = god_variable(comps1)
    r2 = god_variable(comps2)
    assert approx(r1, r2), "Order of components must not change the result"


# CLAIM: GLB-1 (Global coherence — grouping/associativity should not change the aggregate)
def test_associativity_approx():
    # Grouping should be approximately associative for a weighted average
    A = {"x": 0.2, "y": 0.8}
    B = {"z": 0.4, "w": 0.6}

    # One-shot aggregation over all components
    r_all = god_variable({**A, **B})

    # Two-step: aggregate A and B separately (with equal weight),
    # then mix those two aggregate scores.
    r_A = god_variable(A)
    r_B = god_variable(B)
    r_two = god_variable({"A": r_A, "B": r_B})

    assert approx(r_all, r_two, tol=1e-9), "Aggregation should be approx-associative"


# CLAIM: GLB-1 (Global coherence — increasing a component must not reduce the score)
def test_monotonicity():
    base = {"a": 0.2, "b": 0.3, "c": 0.4}
    low = god_variable(base)

    # Increase one component (others unchanged) -> output should not decrease
    higher = {**base, "b": 0.9}
    high = god_variable(higher)
    assert high >= low, "Increasing a component must not reduce the score"


# CLAIM: GLB-1 (Global coherence — weights modulate influence predictably, like couplings)
def test_weighting_effect():
    comps = {"a": 0.2, "b": 0.9}
    # Heavier weight on 'b' should pull result closer to 0.9
    r_equal = god_variable(comps, weights={"a": 1, "b": 1})
    r_b_heavy = god_variable(comps, weights={"a": 1, "b": 5})
    assert r_b_heavy > r_equal, "Increasing a component's weight should raise its influence"


# CLAIM: GLB-1 (Global coherence — outputs remain within global bounds after clamping)
def test_bounds_respected():
    comps = {"a": -100, "b": 1000}
    r = god_variable(comps, bounds=(0.0, 1.0))
    assert 0.0 <= r <= 1.0, "Aggregation must respect bounds after clamping"


# CLAIM: GLB-1 (Global coherence — robust defaults; missing weights handled without crashing)
def test_missing_weights_default_to_zero_not_crash():

