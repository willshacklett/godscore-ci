#!/usr/bin/env python3
"""
Minimal v0 runtime for GodScore CI.

- Lower GV is better
- GodScore = clamp(1 - GV, 0..1)
- Threshold is applied AFTER computation (not in GVState init)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Iterable
import json


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# -------------------------
# Core Data Structures
# -------------------------

@dataclass
class GVEvent:
    label: str
    penalty: float = 0.0
    notes: str = ""


@dataclass
class GVState:
    gv: float = 0.0
    steps: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)

    def apply(self, event: GVEvent) -> None:
        self.steps += 1
        self.gv += float(event.penalty)
        self.history.append({
            "step": self.steps,
            "label": event.label,
            "penalty": event.penalty,
            "gv_after": self.gv
        })


def godscore_from_gv(gv: float) -> float:
    return clamp(1.0 - gv, 0.0, 1.0)


# -------------------------
# Scenarios
# -------------------------

def stable(steps: int = 10) -> List[GVEvent]:
    return [GVEvent("stable", 0.0) for _ in range(steps)]


def degrade(steps: int = 10, per_step: float = 0.06) -> List[GVEvent]:
    return [GVEvent("degrade", per_step) for _ in range(steps)]


def recover(steps: int = 10, per_step: float = -0.05) -> List[GVEvent]:
    return [GVEvent("recover", per_step) for _ in range(steps)]


def oscillate(cycles: int = 5) -> List[GVEvent]:
    events = []
    for i in range(cycles):
        events.append(GVEvent(f"up_{i+1}", 0.08))
        events.append(GVEvent(f"down_{i+1}", -0.06))
    return events


# -------------------------
# Runner
# -------------------------

def run(name: str, events: Iterable[GVEvent], threshold: float = 1.0) -> Dict[str, Any]:
    state = GVState()

    for e in events:
        state.apply(e)

    gv = state.gv
    godscore = godscore_from_gv(gv)

    return {
        "scenario": name,
        "threshold": threshold,
        "passed": gv <= threshold,
        "gv": gv,
        "godscore": godscore,
        "steps": state.steps,
        "history": state.history
    }


def main():
    threshold = 1.0

    scenarios = {
        "stable": stable(),
        "degrade": degrade(),
        "recover": recover(),
        "oscillate": oscillate()
    }

    results = []
    for name, events in scenarios.items():
        results.append(run(name, events, threshold))

    output = {
        "version": "v0",
        "threshold": threshold,
        "results": results
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
