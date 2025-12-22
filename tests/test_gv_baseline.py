import math
import pytest

from gv_baseline.godscore import godscore, GVConfig


def test_score_is_bounded():
    s = godscore([5.0], [1.0])
    assert 0.0 < s < 1.0


def test_more_order_increases_score():
    base = godscore([1.0, 1.0], [1.0, 1.0])
    higher = godscore([3.0, 3.0], [1.0, 1.0])
    assert higher > base


def test_more_entropy_decreases_score():
    base = godscore([3.0, 3.0], [1.0, 1.0])
    worse = godscore([3.0, 3.0], [4.0, 4.0])
    assert worse < base


def test_equal_order_entropy_is_half():
    cfg = GVConfig(alpha=1.0, beta=1.0, gamma=1.0)
    s = godscore([5.0], [5.0], cfg)
    assert math.isclose(s, 0.5, abs_tol=1e-9)


def test_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        godscore([], [1.0])

    with pytest.raises(ValueError):
        godscore([1.0], [])

    with pytest.raises(ValueError):
        godscore([-1.0], [1.0])
