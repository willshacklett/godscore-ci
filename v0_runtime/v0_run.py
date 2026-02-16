"""
v0_run.py
Minimal GV runtime demo (no external dependencies)

Run with:
    python v0_run.py
"""

from dataclasses import dataclass
from typing import List


# ---------------------------
# GV Core
# ---------------------------

@dataclass
class GVState:
    penalties: List[float]

    def gv(self) -> float:
        """
        Lower GV is better.
        GV is sum of penalties.
        """
        return sum(self.penalties)

    def godscore(self) -> float:
        """
        GodScore = 1 - GV (clamped between 0 and 1)
        """
        score = 1.0 - self.gv()
        return max(0.0, min(1.0, score))


# ---------------------------
# Scenarios
# ---------------------------

def stable_scenario() -> GVState:
    # Small penalties → stable system
    return GVState(penalties=[0.05, 0.03, 0.02])


def risky_scenario() -> GVState:
    # Larger penalties → degrading system
    return GVState(penalties=[0.30, 0.25, 0.20])


# ---------------------------
# Runner
# ---------------------------

def run(name: str, state: GVState, threshold: float = 0.8):
    gv = state.gv()
    score = state.godscore()

    print(f"\nScenario: {name}")
    print(f"GV: {gv:.3f}")
    print(f"GodScore: {score:.3f}")

    if score < threshold:
        print("⚠️  Below threshold")
    else:
        print("✅ Above threshold")

    return {
        "name": name,
        "gv": gv,
        "godscore": score
    }


def main():
    results = []
    results.append(run("stable", stable_scenario()))
    results.append(run("risky", risky_scenario()))

    print("\nDone.")
    return results


if __name__ == "__main__":
    main()
