from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class ComponentScore:
    name: str
    score: float  # 0..1 (higher is better)
    weight: float  # >= 0


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _weighted_mean(components: list[ComponentScore]) -> float:
    total_w = sum(c.weight for c in components)
    if total_w <= 0:
        return 0.0
    return sum(c.score * c.weight for c in components) / total_w


def score_project(project_path: str | Path) -> Dict[str, Any]:
    """
    Deterministic starter scoring (fast + reproducible).
    This is a stable scaffold we can later swap to your deeper Gv logic.

    Components:
    - auditability: README/LICENSE/tests present
    - self_correction: CONTRIBUTING/CODE_OF_CONDUCT/Issue templates present
    - reversibility: placeholder derived from irreversibility_risk (neutral for now)
    """
    p = Path(project_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")
    if not p.is_dir():
        raise NotADirectoryError(f"Not a directory: {p}")

    # Auditability signals
    has_readme = (p / "README.md").exists()
    has_license = (p / "LICENSE").exists() or (p / "LICENSE.md").exists()
    has_tests = (p / "tests").exists() and (p / "tests").is_dir()

    auditability = _clamp01((int(has_readme) + int(has_license) + int(has_tests)) / 3.0)

    # Self-correction signals
    has_contributing = (p / "CONTRIBUTING.md").exists()
    has_code_of_conduct = (p / "CODE_OF_CONDUCT.md").exists()
    has_issue_templates = (p / ".github" / "ISSUE_TEMPLATE").exists()

    self_correction = _clamp01(
        (int(has_contributing) + int(has_code_of_conduct) + int(has_issue_templates)) / 3.0
    )

    # Placeholder for now (we’ll replace with your real irreversibility checks)
    irreversibility_risk = 0.5  # 0 good, 1 bad
    reversibility = 1.0 - irreversibility_risk

    components = [
        ComponentScore("auditability", auditability, 0.40),
        ComponentScore("self_correction", self_correction, 0.40),
        ComponentScore("reversibility", reversibility, 0.20),
    ]

    gv_score = _clamp01(_weighted_mean(components))

    return {
        "schema_version": "0.1",
        "project_path": str(p),
        "gv_score": round(gv_score, 4),
        "components": {
            "auditability": round(auditability, 4),
            "self_correction": round(self_correction, 4),
            "irreversibility_risk": round(irreversibility_risk, 4),
            "reversibility": round(reversibility, 4),
        },
        "weights": {c.name: c.weight for c in components},
        "notes": [
            "Deterministic scaffold (starter engine).",
            "Next: replace irreversibility_risk placeholder with real scoring from your gate/orchestrator logic.",
        ],
    }
