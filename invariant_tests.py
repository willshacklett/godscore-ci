# --- invariant_tests.py -------------------------------------------------------
from copy import deepcopy
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

Number = Union[int, float]

# ---------- utilities ----------

def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x))

def _is_finite_number(x: Any) -> bool:
    return _is_number(x) and math.isfinite(float(x))

def is_finite_structure(x: Any) -> bool:
    """Recursively ensure no NaN/Inf anywhere."""
    if _is_number(x):
        return _is_finite_number(x)
    if isinstance(x, (list, tuple)):
        return all(is_finite_structure(v) for v in x)
    if isinstance(x, dict):
        return all(is_finite_structure(v) for v in x.values())
    return True  # non-numeric types are fine

def within_range_structure(x: Any, lo: float, hi: float) -> bool:
    """If numeric, enforce lo<=x<=hi; recurse into containers."""
    if _is_number(x):
        return (lo <= float(x) <= hi)
    if isinstance(x, (list, tuple)):
        return all(within_range_structure(v, lo, hi) for v in x)
    if isinstance(x, dict):
        return all(within_range_structure(v, lo, hi) for v in x.values())
    return True  # non-numeric types ignored

def generic_equal(a: Any, b: Any, tol: float = 0.0) -> bool:
    """Equality with tolerance for numbers; deep equals for containers."""
    if _is_number(a) and _is_number(b):
        return abs(float(a) - float(b)) <= tol
    if type(a) != type(b):
        return False
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(generic_equal(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(generic_equal(a[k], b[k], tol) for k in a)
    return a == b

# ---------- reporting ----------

class InvariantResult:
    def __init__(self, index: int, deterministic: bool, finite: bool, in_range: Optional[bool]):
        self.index = index
        self.deterministic = deterministic
        self.finite = finite
        self.in_range = in_range

    @property
    def passed(self) -> bool:
        ok = self.deterministic and self.finite
        if self.in_range is not None:
            ok = ok and self.in_range
        return ok

class InvariantReport:
    def __init__(self, results: List[InvariantResult], expected_range: Optional[Tuple[float, float]]):
        self.results = results
        self.expected_range = expected_range

    @property
    def pass_rate(self) -> float:
        return 0.0 if not self.results else sum(r.passed for r in self.results) / len(self.results)

    @property
    def fail_count(self) -> int:
        return 0 if not self.results else sum(1 for r in self.results if not r.passed)

    def summary(self) -> Dict[str, Any]:
        det_fail = sum(1 for r in self.results if not r.deterministic)
        fin_fail = sum(1 for r in self.results if not r.finite)
        rng_fail = sum(1 for r in self.results if (r.in_range is False))
        return {
            "count": len(self.results),
            "pass_rate": self.pass_rate,
            "fail_count": self.fail_count,
            "determinism_failures": det_fail,
            "finite_failures": fin_fail,
            "range_checked": self.expected_range is not None,
            "range_failures": rng_fail,
            "expected_range": self.expected_range,
        }

# ---------- main suite ----------

def run_invariant_suite(
    interactions: List,                     # List[Interaction]
    model_fn: Callable[[Any, Dict[str, Any]], Any],
    *,
    repeats: int = 3,
    tol: float = 0.0,                       # numeric tolerance for determinism
    expected_range: Optional[Tuple[float, float]] = None
) -> InvariantReport:
    results: List[InvariantResult] = []

    for idx, inter in enumerate(interactions):
        x = deepcopy(inter.input_data)
        ctx = deepcopy(inter.context or {})

        # run multiple times on identical input/context
        outs = [model_fn(deepcopy(x), deepcopy(ctx)) for _ in range(repeats)]

        # determinism: all outputs equal (within tol for numbers)
        deterministic = all(generic_equal(outs[0], y, tol) for y in outs[1:])

        # finiteness: no NaN/Inf anywhere
        finite = all(is_finite_structure(y) for y in outs)

        # optional range check
        in_range = None
        if expected_range is not None:
            lo, hi = expected_range
            in_range = all(within_range_structure(y, lo, hi) for y in outs)

        results.append(InvariantResult(idx, deterministic, finite, in_range))

    return InvariantReport(results, expected_range)
# -------------------------------------------------------------------------------
# CLAIM: GLB-1 (Global coherence — determinism, finiteness, and range compliance for the God Variable)
