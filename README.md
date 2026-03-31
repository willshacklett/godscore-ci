# GodScore CI

GodScore CI turns CI into a trust signal with memory.

Instead of only asking whether a build passes right now, it asks:
is this system still recoverable over time?

---

## The shift

Traditional CI:
- pass / fail
- snapshot checks
- green = “looks fine right now”

GodScore CI:
- tracks trajectory
- detects loss of recoverability
- blocks when systems drift into irreversibility

Even when a repo still looks green, GodScore CI can detect that it’s already breaking.

---

## Core model

Runtime signal structure:

- spike -> candidate
- persistence + failed recovery -> confirmation
- entropy velocity -> transient veto only
- adaptive dS/dt -> noise-aware gating
- fusion -> final trust boundary

---

## Status semantics

- SAFE -> system trajectory is stable
- AT RISK -> early warning / degrading recoverability
- CRITICAL -> irreversibility detected -> CI FAIL

---

## Enforcement behavior

Closed loop:

trajectory -> runtime signal -> drift -> adaptive -> fusion -> CI decision

CI behavior:

- SAFE -> PASS
- AT RISK -> WARN
- CRITICAL -> FAIL

---

## Dashboard

Runtime view:

https://willshacklett.github.io/godscore-ci/dashboard/runtime/index.html

Shows:
- fused status
- fused score
- runtime score
- adaptive threshold
- warning history

---

## What makes this different

Most CI systems answer:

Did this pass?

GodScore CI answers:

Should we still trust this system?

---

## Capabilities

- static trust scoring
- runtime irreversibility detection
- drift detection
- adaptive thresholds
- fused decision layer
- dashboard visibility
- CI enforcement

---

## Quick start

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-runtime.txt

python scripts/runtime_signal.py examples/runtime_signal_input.csv

Open:

/dashboard/runtime/index.html

---

## Positioning

- CI with memory
- trajectory-aware enforcement
- recoverability-aware systems
- early failure detection

---

## Taglines

- Honesty over green lights
- Trends matter more than snapshots
- Detect failure before failure
- CI that understands trajectory

---

## Status

Production-ready for:
- real-world testing
- CI enforcement experiments
- early adopters

---

## License

See repository license.
