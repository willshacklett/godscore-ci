# --- ablation_tests.py --------------------------------------------------------
# Compare a "god_model_fn" (with the God variable) against a "baseline_fn"
# (same task, but *without* the God variable). Uses the InteractionLog's
# recorded output_data as the target/ground-truth when available.

from copy import deepcopy
import math
import random
import statistics
from typing import Any, Callable, Dict, List, Optional, Tuple

# -------------------------
# Generic distance / loss
# -------------------------

def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x))

def _safe_rel_err(a: float, b: float, eps: float = 1e-12) -> float:
    denom = max(abs(a), abs(b), eps)
    return abs(a - b) / denom

def _str_sim(a: str, b: str) -> float:
    # Cheap similarity proxy to avoid importing difflib.
    # Returns [0,1], 1 == identical
    if a == b:
        return 1.0
    # token overlap Jaccard-ish
    A = set(str(a))
    B = set(str(b))
    if not A and not B:
        return 1.0
    return len(A & B) / max(1, len(A | B))

def generic_distance(a: Any, b: Any) -> float:
    """
    Distance-like score; lower is better (0 == identical).
    - Numbers: relative error
    - Strings: 1 - similarity
    - Sequences/Dicts: average element-wise distance (order-sensitive for lists)
    - Fallback: 0 if equal else 1
    """
    if _is_number(a) and _is_number(b):
        return _safe_rel_err(float(a), float(b))

    if isinstance(a, str) or isinstance(b, str):
        return 1.0 - _str_sim(str(a), str(b))

    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        n = max(len(a), len(b))
        if n == 0:
            return 0.0
        a_pad = list(a) + [None] * (n - len(a))
        b_pad = list(b) + [None] * (n - len(b))
        return sum(generic_distance(x, y) for x, y in zip(a_pad, b_pad)) / n

    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a.keys()) | set(b.keys())
        if not keys:
            return 0.0
        return sum(generic_distance(a.get(k), b.get(k)) for k in keys) / len(keys)

    return 0.0 if a == b else 1.0

# -------------------------
# Ablation result/report
# -------------------------

class AblationRow:
    def __init__(self, index: int, target_present: bool, baseline_loss: Optional[float], god_loss: Optional[float]):
        self.index = index
        self.target_present = target_present
        self.baseline_loss = baseline_loss
        self.god_loss = god_loss

    @property
    def delta(self) -> Optional[float]:
        """Positive delta means God model improved (baseline_loss - god_loss)."""
        if self.baseline_loss is None or self.god_loss is None:
            return None
        return self.baseline_loss - self.god_loss

class AblationReport:
    def __init__(self, rows: List[AblationRow]):
        self.rows = rows

    def _vals(self, attr: str) -> List[float]:
        return [getattr(r, attr) for r in self.rows if getattr(r, attr) is not None]

    @property
    def count(self) -> int:
        return len([r for r in self.rows if r.target_present and r.baseline_loss is not None and r.god_loss is not None])

    @property
    def mean_baseline(self) -> Optional[float]:
        xs = self._vals("baseline_loss")
        return statistics.mean(xs) if xs else None

    @property
    def mean_god(self) -> Optional[float]:
        xs = self._vals("god_loss")
        return statistics.mean(xs) if xs else None

    @property
    def mean_delta(self) -> Optional[float]:
        ds = self._vals("delta")
        return statistics.mean(ds) if ds else None

    @property
    def win_rate(self) -> Optional[float]:
        """Fraction of examples where god_loss < baseline_loss."""
        good = [r for r in self.rows if r.baseline_loss is not None and r.god_loss is not None]
        if not good:
            return None
        wins = sum(1 for r in good if r.god_loss < r.baseline_loss)
        return wins / len(good)

    def bootstrap_ci(self, n_boot: int = 1000, seed: int = 42, which: str = "delta", alpha: float = 0.05) -> Optional[Tuple[float, float]]:
        vals = self._vals(which)
        if not vals:
            return None
        random.seed(seed)
        n = len(vals)
        samples = []
        for _ in range(n_boot):
            draw = [vals[random.randrange(n)] for _ in range(n)]
            samples.append(statistics.mean(draw))
        samples.sort()
        lo_idx = int((alpha/2) * (n_boot - 1))
        hi_idx = int((1 - alpha/2) * (n_boot - 1))
        return (samples[lo_idx], samples[hi_idx])

    def summary(self) -> Dict[str, Any]:
        ci = self.bootstrap_ci(which="delta")  # 95% CI on mean delta
        return {
            "n_evaluated": self.count,
            "mean_baseline_loss": self.mean_baseline,
            "mean_god_loss": self.mean_god,
            "mean_delta": self.mean_delta,          # >0 means God model better
            "delta_95pct_CI": ci,
            "win_rate": self.win_rate,              # fraction where God beats baseline
        }

# -------------------------
# Main ablation runner
# -------------------------

def run_ablation_suite(
    interactions: List,                                   # List[Interaction]
    god_model_fn: Callable[[Any, Dict[str, Any]], Any],   # with God variable
    baseline_fn: Callable[[Any, Dict[str, Any]], Any],    # without God variable
    *,
    loss_fn: Callable[[Any, Any], float] = generic_distance,  # loss(pred, target); lower is better
    skip_if_no_target: bool = True
) -> AblationReport:
    """
    For each interaction with target (interaction.output_data):
      baseline_pred = baseline_fn(input, context)
      god_pred      = god_model_fn(input, context)
      baseline_loss = loss_fn(baseline_pred, target)
      god_loss      = loss_fn(god_pred, target)
      Record delta = baseline_loss - god_loss  (positive means improvement)

    If skip_if_no_target==False, entries without target will be ignored gracefully anyway.
    """
    rows: List[AblationRow] = []

    for idx, inter in enumerate(interactions):
        x = deepcopy(inter.input_data)
        ctx = deepcopy(inter.context or {})
        has_target = hasattr(inter, "output_data") and (inter.output_data is not None)

        if not has_target and skip_if_no_target:
            continue

        baseline_pred = baseline_fn(deepcopy(x), deepcopy(ctx))
        god_pred = god_model_fn(deepcopy(x), deepcopy(ctx))

        baseline_loss = loss_fn(baseline_pred, inter.output_data) if has_target else None
        god_loss = loss_fn(god_pred, inter.output_data) if has_target else None

        rows.append(AblationRow(index=idx, target_present=has_target, baseline_loss=baseline_loss, god_loss=god_loss))

    return AblationReport(rows)
# ------------------------------------------------------------------------------
