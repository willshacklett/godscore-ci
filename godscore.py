"""
Baseline God Variable implementation.

This module defines the minimal, explicit contract for the God Variable (Gv).
The goal is not moral authority, but preservation of long-term system
survivability, corrigibility, and reversibility.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class GodVariableResult:
    score: float
    penalties: Dict[str, float]


class GodVariable:
    """
    The God Variable evaluates system behaviors and applies penalties
    when actions undermine long-term survivability.

    Higher scores indicate healthier systems.
    """

    def __init__(self, base_score: float = 1.0):
        self.base_score = base_score

    def evaluate(self, signals: Dict[str, float]) -> GodVariableResult:
        """
        Evaluate system signals and compute a God Variable score.

        Expected signals (all optional, range 0.0–1.0):
        - irreversible_harm
        - correction_suppression
        - short_term_overoptimization
        """

        penalties = {}

        if signals.get("irreversible_harm", 0) > 0:
            penalties["irreversible_harm"] = signals["irreversible_harm"] * 0.5

        if signals.get("correction_suppression", 0) > 0:
            penalties["correction_suppression"] = signals["correction_suppression"] * 0.3

        if signals.get("short_term_overoptimization", 0) > 0:
            penalties["short_term_overoptimization"] = signals["short_term_overoptimization"] * 0.2

        total_penalty = sum(penalties.values())
        score = max(0.0, self.base_score - total_penalty)

        return GodVariableResult(score=score, penalties=penalties)
