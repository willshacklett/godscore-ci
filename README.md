# GodScore CI

GodScore CI turns CI into a trust signal with memory.

Instead of only asking whether a build passes right now, GodScore CI asks whether the system is still recoverable over time.

Live Dashboard  
https://willshacklett.github.io/godscore-ci/dashboard/

## What it does

GodScore CI assigns a normalized trust score (0–100) and can now incorporate a runtime irreversibility signal.

Core layers:
- static CI score -> snapshot quality
- runtime signal -> trajectory risk
- drift detection -> repeated non-recoverability
- adaptive threshold -> context-aware enforcement
- fusion -> one final trust boundary

This means a system can fail CI even when snapshot checks are still green, if trajectory-level recoverability has already broken down.

## Runtime signal shape

Current runtime logic:

- spike -> candidate
- persistence + failed recovery -> confirmation
- adaptive dS/dt -> noise-aware candidate gating
- entropy velocity -> transient veto only
- fusion -> final trust boundary

## Status semantics

- SAFE -> system trajectory looks stable
- AT RISK -> early warning / degrading recoverability
- CRITICAL -> irreversibility signal strong enough to block CI

## Why this matters

Traditional CI is mostly snapshot-based:
- pass / fail
- lint / tests
- coverage / static checks

GodScore CI adds:
- recoverability
- trend memory
- irreversibility detection
- runtime-aware enforcement

In short:

GodScore CI is not just “did it pass?”
It is “is this system still safe to trust?”

## Current product surface

### 1. Static score
A normalized GodScore-style score for trust / survivability.

### 2. Runtime signal
A trajectory-aware signal that detects non-recoverability before visible failure.

### 3. Drift detection
Looks for persistent degradation across repeated runtime checks.

### 4. Adaptive enforcement
Thresholds adjust to system volatility instead of using a single rigid line.

### 5. Fusion layer
Combines static + runtime into one final decision boundary.

### 6. Dashboard
Published dashboard view with:
- fused status
- fused score
- runtime score
- threshold
- warning history

## Current dashboard views

Main:
- https://willshacklett.github.io/godscore-ci/dashboard/

Runtime:
- https://willshacklett.github.io/godscore-ci/dashboard/runtime/index.html

## Workflow behavior

Current fused behavior:

- SAFE -> pass
- AT RISK -> warn
- CRITICAL -> fail

This gives teams a visible, explainable, trajectory-aware CI gate.

## Quick start

### Local runtime demo
1. Create and activate a venv
2. Install runtime requirements
3. Run the runtime signal
4. Inspect outputs and dashboard

Example:

python3 -m venv .venv  
source .venv/bin/activate  
pip install -r requirements-runtime.txt  
python scripts/runtime_signal.py examples/runtime_signal_input.csv

### GitHub Actions
Run:
- Runtime Signal Demo

This produces:
- runtime score
- drift summary
- adaptive summary
- fused summary
- dashboard-visible artifacts

## Positioning

GodScore CI is best understood as:

- trajectory-aware CI
- recoverability-aware enforcement
- trust scoring with memory
- early irreversibility detection for software systems

## Tagline options

- Honesty over green lights
- Trends matter more than snapshots
- Detect failure before failure
- CI with memory
- Recoverability-aware enforcement

## Current maturity

This repo now supports:
- advisory runtime scoring
- fused runtime/static view
- dashboard visibility
- workflow-level fused enforcement

That makes it suitable for real-world pressure testing and early adopter usage.

## License

See repository license.
