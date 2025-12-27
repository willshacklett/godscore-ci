# GodScore CI

**Survivability-Aware Continuous Integration**

GodScore CI is an experimental, open framework for evaluating **long-term system survivability** inside automated development pipelines.

Traditional CI systems answer short-term questions:

- Does the code compile?
- Do tests pass?
- Is performance acceptable right now?

GodScore CI asks a different question:

> **Does this change reduce the system’s ability to survive, self-correct, or recover over time?**

---

## What GodScore Measures

GodScore CI evaluates a single scalar metric — the **God Variable (Gv)** — representing aggregate survivability signals such as:

- **Auditability** – Can behavior be inspected and understood?
- **Reversibility** – Can changes be undone or corrected?
- **Irreversibility Risk** – Does this introduce permanent failure modes?
- **Self-Correction Capacity** – Can the system adapt after error?

These components are combined into a normalized score (`0.0 – 1.0`) that can be:
- reported to humans
- enforced by policy
- tracked over time

The metric is intentionally simple, inspectable, and extensible.

---

## How It Works

GodScore CI integrates directly into GitHub Actions:

1. A scoring engine evaluates the repository
2. A machine-readable report (`gv_report.json`) is generated
3. A human-readable report (`gv_report.md`) is produced
4. CI gates may **enforce minimum survivability thresholds**
5. Pull requests receive an automatic comment with the current Gv score

The result is a survivability signal that is:
- automated
- repeatable
- visible at review time
- enforceable without manual judgment

---

## Why Survivability?

Many system failures are not caused by bugs — they are caused by:
- irreversible design decisions
- suppressed correction paths
- brittle optimization
- loss of auditability over time

GodScore CI does not attempt to define *correct behavior*.
It attempts to preserve the conditions under which **correction remains possible**.

This makes it applicable to:
- complex software systems
- safety-critical tooling
- AI and autonomous systems
- long-lived infrastructure

---

## Philosophy (Briefly)

GodScore CI is **not**:
- a moral authority
- an ideology
- a claim about truth or intent

It is a tooling framework that encodes one principle:

> **Systems that cannot correct themselves do not remain safe.**

---

## Status

GodScore CI is **experimental**.

- The current scoring model is a stable scaffold
- Components are expected to evolve
- Thresholds are policy decisions, not truths

The project prioritizes clarity, auditability, and gradual refinement over rapid expansion.

---

## Usage

### Run locally
```bash
python -m pip install -e .
python -m godscore_ci.cli score . --outdir gv_out
