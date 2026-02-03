# godscore_ci/scoring_pipeline.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from godscore_ci.autoscore_v1 import compute_autoscore_v1
from godscore_ci.gv_engine import compute_gv, GVResult


@dataclass
class ScorePipelineResult:
    # normalized 0.0–1.0
    godscore: float
    gv: float
    penalties: Dict[str, float]
    notes: List[str]
    gv_explanation: List[str]
    signals: Dict[str, object]
    source: str  # "auto" or "manual"


def parse_score_input(raw_score: Optional[str]) -> Tuple[bool, Optional[float]]:
    """
    Returns (use_auto, score_value)
    score_value is normalized 0..1 if present.
    """
    if raw_score is None:
        return True, None

    s = str(raw_score).strip()
    if s == "" or s.lower() == "auto":
        return True, None

    # allow 0–100 or 0–1 inputs
    val = float(s)
    if val > 1.0:
        val = val / 100.0
    return False, max(0.0, min(1.0, val))


def compute_score_pipeline(
    raw_score: Optional[str] = None,
    base_sha: Optional[str] = None,
    head_sha: Optional[str] = None,
    weights: Optional[Dict[str, float]] = None,
) -> ScorePipelineResult:
    """
    If raw_score is missing/auto -> compute AutoScore v1 penalties, then GV -> GodScore
    If raw_score provided -> use it directly as GodScore but still provide minimal metadata.
    """
    use_auto, manual_score = parse_score_input(raw_score)

    if not use_auto and manual_score is not None:
        # Manual path: keep it simple, no pretending.
        return ScorePipelineResult(
            godscore=manual_score,
            gv=max(0.0, min(1.0, 1.0 - manual_score)),
            penalties={},
            notes=[f"User-provided score: {manual_score:.2f} (normalized 0..1)"],
            gv_explanation=[f"GodScore = {manual_score:.2f}", f"GV = {1.0 - manual_score:.2f} (derived)"],
            signals={},
            source="manual",
        )

    # Auto path:
    auto = compute_autoscore_v1(base_sha=base_sha, head_sha=head_sha)

    gv_res: GVResult = compute_gv(auto.penalties, weights=weights)

    notes = []
    notes.append("AutoScore v1 active (computed penalties -> GV -> GodScore).")
    notes.extend(auto.notes)

    return ScorePipelineResult(
        godscore=gv_res.godscore,
        gv=gv_res.gv,
        penalties=auto.penalties,
        notes=notes,
        gv_explanation=gv_res.explanation,
        signals=auto.signals,
        source="auto",
    )
