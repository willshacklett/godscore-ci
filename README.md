[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-GodScore%20CI-blue?logo=github)](https://github.com/marketplace/actions/godscore-ci)
[![Latest Release](https://img.shields.io/github/v/release/willshacklett/godscore-ci)](https://github.com/willshacklett/godscore-ci/releases)

# GodScore CI

A survivability-aware CI gate that detects long-term system risk before it reaches production.

GodScore CI turns survivability signals into optional warnings or non-optional guardrails inside your CI pipeline.

---

## Pricing

Free tier:
- Generates a GodScore
- Prints guidance in CI
- Never blocks builds

Paid tier ($10/month per repo):
- Enables enforcement
- Can fail the build when risk is too high

Free informs. Paid enforces.

---

## Install in 30 Seconds

Add this step to any GitHub Actions workflow:

    - name: GodScore CI
      uses: willshacklett/godscore-ci@v0.2.5
      with:
        score: "0.75"
        threshold: "0.70"
        enforce: "false"  # set true to enable enforcement

Commit and push.
GodScore CI will run automatically on every workflow execution.

---

## Enforcement Mode

By default, GodScore CI runs in advisory mode and will not fail your build.

When enforcement mode is enabled (paid tier), GodScore CI applies an opinionated default policy:

- Fail the build if godscore < threshold

This threshold is intentionally opinionated.
A low GodScore indicates elevated systemic risk and should be reviewed before deployment.

Enforcement is always an explicit opt-in.

---

## Quick Start (5 minutes)

Want to see GodScore CI pass and fail immediately?

See the ./examples directory for minimal passing and failing workflows.

Copy one file, commit, and watch CI decide whether the system survives.

---

## What Is GodScore CI?

GodScore CI is a constraint-based Continuous Integration (CI) framework designed to detect irreversible or long-term degradation in evolving systems — issues that traditional CI pipelines often miss.

Rather than asking:

“Does this change work right now?”

GodScore CI asks:

“Does this change reduce the system’s ability to survive, recover, or self-correct over time?”

---

## Core Concept: The God Variable (Gv)

At the heart of the framework is the God Variable (Gv) —
a scalar metric intended to summarize a system’s survivability, self-correctability, and irreversibility risk.

- Higher Gv → greater long-term resilience
- Lower Gv → increased risk of silent degradation or irreversible failure

The GodScore is the computed instantiation of Gv at a given point in time, evaluated before and after proposed changes.

GodScore CI treats regressions in Gv as first-class failures, even when traditional tests pass.

---

## Why This Exists

Modern systems often fail through:

- Cumulative technical debt
- Gradual erosion of recovery paths
- Silent loss of reversibility
- Optimization for short-term success at long-term cost

Traditional CI pipelines are excellent at enforcing local correctness.
GodScore CI extends this by enforcing global survivability constraints.

---

## How It Works

GodScore CI integrates into GitHub Actions and evaluates changes using:

- Threshold checks to enforce minimum survivability levels
- Regression awareness based on recent successful runs
- Irreversibility detection
- Clear CI step summaries

If a change causes a meaningful regression in survivability, the CI gate responds based on configured strictness.

---

## CI Gate Modes

Free Mode (default):
- Advisory warnings only
- Ideal for experimentation and learning
- Never blocks merges

Enforcement Mode (paid):
- Fails the build when survivability drops below threshold
- Designed for high-stakes or long-lived systems
- Makes risk non-optional

If it blocks your build, that’s the signal.

---

## GitHub Actions Usage

Free (advisory):

    - name: GodScore CI (Free)
      uses: willshacklett/godscore-ci@v0.2.5
      with:
        score: "0.85"
        threshold: "0.80"
        enforce: "false"

Enforcement (paid):

    - name: GodScore CI (Enforced)
      uses: willshacklett/godscore-ci@v0.2.5
      with:
        score: "0.62"
        threshold: "0.70"
        enforce: "true"

---

## Governance & Survivability (Exploratory)

In addition to detecting long-term system degradation in codebases,
this project explores whether system-level decisions (product, monetization,
policy) can be evaluated against survivability constraints.

The governance/ directory contains non-functional, exploratory material.
These materials do not affect CI behavior.

---

## Status

GodScore CI is actively evolving.

Expect opinionated defaults, sharp edges, and gradual refinement.

If it saves you from one irreversible mistake, it paid for itself.
