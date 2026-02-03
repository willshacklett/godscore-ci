# godscore_ci/gv_engine.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class GVComponent:
    name: str
    value: float        # normalized 0.0 – 1.0
    description: str


@dataclass
class GVResult:
    gv: float            # 0.0 (best) → 1.0 (worst)
    godscore: float      # 1.0 – gv
    components: List[GVComponent]
    explanation: List[str]


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def compute_gv(
    penalties: Dict[str, float],
    weights: Dict[str, float] | None = None,
) -> GVResult:
    """
    penalties: normalized penalty terms (0–1) keyed by component name
    weights: optional weighting per component (defaults to 1.0)
    """

    components: List[GVComponent] = []
    explanation: List[str] = []

    gv_total = 0.0

    for name, penalty in penalties.items():
        w = 1.0 if weights is None else weights.get(name, 1.0)
        p = clamp(penalty)
        contribution = w * p

        gv_total += contribution

        components.append(
            GVComponent(
                name=name,
                value=p,
                description=f"{name} penalty = {p:.2f} (weight {w:.2f})",
            )
        )

        explanation.append(
            f"+{contribution:.2f} from {name} (penalty {p:.2f}, weight {w:.2f})"
        )

    gv = clamp(gv_total)
    godscore = clamp(1.0 - gv)

    explanation.insert(0, f"GV total = {gv:.2f}")
    explanation.append(f"GodScore = {godscore:.2f}")

    return GVResult(
        gv=gv,
        godscore=godscore,
        components=components,
        explanation=explanation,
    )
