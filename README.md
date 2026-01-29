# GodScore CI

## Pricing

**Free tier:** Generates a GodScore and prints guidance in CI (no blocking).

**Paid tier ($10/month per repo):** Enables **enforcement** — configurable thresholds that can **fail the build** when risk is too high.

> Free informs. Paid enforces.

---

## Quick Start (5 minutes)

Want to see GodScore CI work — or fail — immediately?

➡️ **[Minimal passing and failing examples](./examples)**

Copy one file, commit, and watch CI decide whether the system survives.

**GodScore CI** is a constraint-based Continuous Integration (CI) framework designed to detect *irreversible or long-term degradations* in evolving systems—issues that traditional CI pipelines often miss.

Rather than asking “Does this change work right now?”, GodScore CI asks:

> **“Does this change reduce the system’s ability to survive, recover, or self-correct over time?”**

---

## Core Concept: The God Variable (Gv)

At the heart of the framework is the **God Variable (Gv)**:  
a scalar metric intended to summarize a system’s **survivability, self-correctability, and irreversibility risk**.

- **Higher Gv** → greater long-term resilience  
- **Lower Gv** → increased risk of silent degradation or irreversible failure  

The **GodScore** is the computed instantiation of Gv at a given point in time, evaluated before and after proposed changes.

GodScore CI treats regressions in Gv as *first-class failures*, even when traditional tests pass.

---

## Why This Exists

Modern systems often fail through:

- Cumulative technical debt  
- Gradual erosion of recovery paths  
- Silent loss of reversibility  
- Optimization for short-term success at long-term cost  

Traditional CI pipelines are excellent at enforcing **local correctness**.  
GodScore CI extends this by enforcing **global survivability constraints**.

---

## How It Works

GodScore CI integrates into GitHub Actions and evaluates changes using:

- **Invariant tests** – enforce formal properties of Gv  
- **Perturbation tests** – simulate disruptions and recovery  
- **Regression checks** – compare current Gv against historical baselines  
- **Irreversibility detection** – flag non-recoverable state transitions  

If a change causes a meaningful regression in Gv, the CI gate responds based on configured strictness.

---

## CI Gate Modes

- **Free Mode**
  - Emits warnings only
  - Ideal for experimentation and learning
  - Never blocks merges

- **Pro Mode**
  - Enforces hard failures on Gv regression
  - Designed for high-stakes or long-lived systems

### Feedback

Early feedback highlights the value of catching slow system degradation beyond traditional CI tests.

---

## Governance & Survivability (Gv)

In addition to detecting long-term system degradation in codebases,
this project explores whether **system-level changes** (e.g. product,
monetization, or policy decisions) can be evaluated against long-term
survivability constraints.

The `governance/` directory contains **non-functional, exploratory
documentation** and examples illustrating how a survivability scalar
(Gv) could be used to reason about trust, autonomy, and system stability
before irreversible changes are deployed.

These materials are informational and do not affect CI behavior.

---

## GitHub Actions Integration (Reference)

Add GodScore CI to an existing GitHub Actions workflow:

```yaml
name: GodScore CI

on:
  pull_request:
  push:

jobs:
  godscore:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run GodScore CI gate
        uses: willshacklett/godscore-ci@v0.2.4
        with:
          score: "0.85"
          threshold: "0.80"
          mode: "free"
