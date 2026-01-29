# GodScore CI

A survivability-aware CI gate that detects long-term system risk **before** it reaches production.

---

## Pricing

**Free tier:** Generates a GodScore and prints guidance in CI (no blocking).

**Paid tier ($10/month per repo):** Enables **enforcement** — configurable thresholds that can **fail the build** when risk is too high.

> Free informs. Paid enforces.

---

## Enforcement Mode

By default, GodScore CI runs in **advisory mode** and will not fail your build.

When **enforcement mode** is enabled (paid tier), GodScore CI applies an opinionated default policy:

- **Fail the build if `godscore < threshold`**

This threshold is intentionally opinionated.  
A low GodScore indicates elevated systemic risk and should be reviewed before deployment.

Future versions may allow custom thresholds, but enforcement always remains an explicit opt-in.

---

## Quick Start (5 minutes)

Want to see GodScore CI work — or fail — immediately?

➡️ **[Minimal passing and failing examples](./examples)**

Copy one file, commit, and watch CI decide whether the system survives.

---

## What Is GodScore CI?

**GodScore CI** is a constraint-based Continuous Integration (CI) framework designed to detect *irreversible or long-term degradations* in evolving systems — issues that traditional CI pipelines often miss.

Rather than asking:

> “Does this change work right now?”

GodScore CI asks:

> **“Does this change reduce the system’s ability to survive, recover, or self-correct over time?”**

---

## Core Concept: The God Variable (Gv)

At the heart of the framework is the **God Variable (Gv)** —  
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

- **Invariant checks** — enforce formal properties of survivability  
- **Perturbation tests** — simulate disruption and recovery  
- **Regression checks** — compare current GodScore against baselines  
- **Irreversibility detection** — flag non-recoverable transitions  

If a change causes a meaningful regression in Gv, the CI gate responds based on configured strictness.

---

## CI Gate Modes

### Free Mode (default)
- Emits warnings only  
- Ideal for experimentation and learning  
- Never blocks merges  

### Pro Mode (enforcement)
- Fails the build on GodScore regression  
- Designed for high-stakes or long-lived systems  
- Makes risk non-optional  

> Enforcement is intentionally frictional.  
> If it blocks you, that’s the signal.

---

## GitHub Actions Integration

### Free (advisory / warn-only)

```yaml
- name: GodScore CI (Free)
  uses: willshacklett/godscore-ci@v0.2.4
  with:
    score: "0.85"
    threshold: "0.80"
    enforce: "false"
