# GodScore CI

[![Live Dashboard](https://img.shields.io/badge/dashboard-live-blue)](https://willshacklett.github.io/godscore-ci/dashboard/)
[![Enforcement Demo](https://github.com/willshacklett/godscore-ci/actions/workflows/godscore-enforcement-demo.yml/badge.svg)](https://github.com/willshacklett/godscore-ci/actions/workflows/godscore-enforcement-demo.yml)
[![Dashboard Pages](https://github.com/willshacklett/godscore-ci/actions/workflows/godscore-dashboard.yml/badge.svg)](https://github.com/willshacklett/godscore-ci/actions/workflows/godscore-dashboard.yml)

GodScore CI assigns a **single, explainable trust score (0–100)** to every commit.

Unlike traditional pass/fail CI checks, GodScore:
- tracks **quality over time**
- explains **why** the score moved
- supports **governance, recovery, and survivability**

Live dashboard:  
https://willshacklett.github.io/godscore-ci/dashboard/

---

## Why GodScore

Most CI systems answer one question:

Did it pass?

GodScore answers better ones:
- Are we getting healthier or riskier over time?
- What specifically caused this change?
- Can we recover, and how fast?

GodScore turns CI from a binary gate into a **trust signal with memory**.

---

## Enforcement demo

GodScore CI runs in two modes:

**Free (inform / warn)**
- Prints guidance
- Never blocks builds

**Paid (enforce / fail)**
- Can fail the build when trust drops below a threshold

Example workflow usage:

    - uses: willshacklett/godscore-ci@v0.2.6
      with:
        score: "0.30"
        threshold: "0.80"
        mode: "free"
        enforce: "false"

    - uses: willshacklett/godscore-ci@v0.2.6
      with:
        score: "0.30"
        threshold: "0.80"
        mode: "pro"
        enforce: "true"

**Free informs. Paid enforces.**

The included *GodScore Enforcement Demo* workflow intentionally fails in enforcement mode to prove the gate blocks when GodScore is below threshold.

---

## Dashboard

GodScore CI automatically publishes a live dashboard showing:
- latest GodScore
- historical trend
- commit-level history
- explanation of score changes
- enforcement context

The dashboard updates on every push via GitHub Actions.

---

## Pricing

**Free tier**
- Generates a GodScore
- Prints guidance in CI logs
- Shows dashboard and history
- Never blocks builds

**Paid tier ($10/month per repo)**
- Enables enforcement mode
- Can fail builds when trust drops too low
- Designed for governance and policy use

**Free informs. Paid enforces.**

---

## Inputs

- **score** — GodScore to evaluate (0–1 or 0–100)
- **threshold** — Minimum acceptable score
- **min_score** — Alias for threshold
- **mode** — free (warn) or pro (fail)
- **enforce** — Explicit enforcement toggle
- **pro_token** — Optional future-use token

---

## Outputs

- **passed** — Whether the gate passed
- **effective_mode** — Resolved mode
- **effective_threshold** — Threshold used
- **provided_score** — Score evaluated

---

## Design philosophy

- Honesty over green lights
- Trends matter more than snapshots
- Governance is about recovery, not punishment

---

## Roadmap

- True GodScore engine integration
- Component-level breakdowns
- Organization-wide dashboards
- Compliance exports
- Enterprise licensing

---

## Author

William Shacklett

GodScore CI is not about stopping change.  
It’s about surviving it.
