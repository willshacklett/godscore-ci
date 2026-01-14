# GodScore Demo — Recoverability vs Correctness

This demo illustrates a class of changes that **traditional CI cannot see**, but that **reduce long-term recoverability** of a system.

Nothing is broken.  
All tests pass.  
Yet the system becomes harder to safely change in the future.

That is the gap GodScore CI is designed to surface.

---

## What This Demo Shows

The demo consists of a small Python module with a clean separation:

- `engine.py` contains core business logic
- `adapters.py` contains external concerns (I/O, printing)
- Tests validate correctness only

This separation represents a **recoverable baseline**.

---

## Baseline State (All Green)

In the baseline:

- Tests pass
- `engine` does **not** depend on `adapters`
- Rollbacks and future refactors are localized
- GodScore CI reports a stable score

Traditional CI and GodScore CI are both green.

---

## The Refactor

A refactor is introduced that looks reasonable and even convenient:

- `engine.py` imports `adapters.py`
- A helper function is added to reduce boilerplate
- No behavior changes
- No tests change
- All tests still pass

From a correctness standpoint, nothing is wrong.

---

## What Changed (But CI Can’t See)

The refactor introduces **structural coupling**:

- Core logic now depends on external concerns
- Rollbacks become coordinated instead of isolated
- Optionality is reduced
- Future refactors carry higher risk

This is not a bug.
It is a **loss of recoverability**.

---

## Why GodScore CI Exists

Traditional CI asks:

> “Does the system still work?”

GodScore CI asks:

> “Is the system still safe to change later?”

GodScore does **not** block “bad architecture.”
It detects **negative trajectory** relative to an accepted baseline.

If recoverability decreases beyond a configured threshold,
the gate fails — even when tests are green.

---

## Important Note About Baselines

GodScore CI compares changes **relative to a baseline**.

If a system is already tightly coupled when the baseline is set,
GodScore will not retroactively punish it.

Instead, it protects the system from getting **worse over time**.

This mirrors real-world long-lived systems:
the goal is not purity, but **preventing silent degradation**.

---

## Takeaway

This demo demonstrates a simple but critical idea:

> Not all regressions break correctness.  
> Some break the future.

GodScore CI exists to surface those moments early —
before they compound into irreversible cost.
Add godscore-demo folder
