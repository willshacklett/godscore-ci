# GodScore CI

GodScore CI assigns a single, explainable trust score (0–100) to every commit and tracks how that trust changes over time.

Live Dashboard  
https://willshacklett.github.io/godscore-ci/dashboard/

Enforcement Demo Workflow  
See .github/workflows/godscore-enforcement-demo.yml

Dashboard Source (GitHub Pages)  
https://github.com/willshacklett/godscore-ci/tree/main/dashboard

---

## What it does

GodScore CI turns CI into a trust signal with memory.

Unlike traditional pass/fail CI checks, GodScore CI:

- Tracks quality and risk over time
- Explains why trust moved
- Supports governance, recovery, and survivability
- Can optionally enforce when risk crosses a threshold

Each run produces:
- GodScore — normalized trust score
- Explanation — contributing factors
- History — trend across commits
- Optional enforcement — block builds when trust drops too low

---

## The scoring spine: GV (God Variable)

GodScore CI is powered by GV (God Variable) — a universal scalar that measures:

Loss of recoverability under constraint

- Lower GV is better
- GodScore = 1 − GV
- GV aggregates explainable penalty components
- GV is designed to apply across domains (code today, AI and safety systems next)

GV does not judge intent, correctness, or morality.  
It measures whether a system is becoming harder to recover safely over time.

---

## Quick Start

Inform-only (free)

Example workflow step:

    - uses: actions/checkout@v4

    - name: GodScore CI (AutoScore v1)
      uses: willshacklett/godscore-ci@v0.2.6
      with:
        threshold: "0.80"
        mode: "free"
        enforce: "false"

That’s it.

GodScore CI will compute a score, explain it in logs, and update the dashboard without blocking your build.

---

## Manual score input (still supported)

Example:

    - uses: willshacklett/godscore-ci@v0.2.6
      with:
        score: "0.85"      # or "85"
        threshold: "0.80"  # or "80"
        mode: "free"

Inputs accept 0–1 or 0–100.  
All values are normalized internally.

---

## Why GodScore

Most CI systems answer one question:

Did it pass?

GodScore answers better ones:

- Are we getting healthier or riskier over time?
- What specifically caused this change?
- Can we recover — and how fast?
- Is risk becoming irreversible?

GodScore turns CI from a binary gate into a trust signal with memory.

---

## AutoScore v1 (default scoring)

When score is omitted or set to auto, AutoScore v1 computes penalties automatically and feeds them into GV.

AutoScore v1 currently uses:

- Diff size (lines added + deleted)
- Risky paths touched (src/, lib/, app/, api/, infra/)
- High-risk areas (auth, security, payments, billing)
- Process signals:
  - WIP / tmp / draft commits
  - Tests detected (or not)
  - Reverts (small recovery credit)

These signals become normalized penalty components that GV aggregates into a single GodScore.

---

## Enforcement

GodScore CI supports two modes.

Free — inform only:
- Prints guidance in CI logs
- Updates dashboard
- Never blocks builds

Pro — enforce:
- Can fail the build when trust drops below threshold
- Designed for governance and policy use

Example enforcement step:

    - uses: willshacklett/godscore-ci@v0.2.6
      with:
        threshold: "0.80"
        mode: "pro"
        enforce: "true"

Free informs. Paid enforces.

The included enforcement demo workflow intentionally fails in enforcement mode to prove the gate blocks when GodScore is below threshold.

---

## Score scale and precedence

Scale:
- Inputs accept 0–1 or 0–100
- Outputs are normalized 0–1
- Logs print both normalized and human-readable values

Precedence:
1. If score is provided, it is evaluated directly
2. If score is omitted or auto, AutoScore v1 → GV → GodScore
3. Enforcement triggers only when:
   - mode = pro
   - enforce = true
   - score < threshold

---

## Dashboard

GodScore CI automatically publishes a live dashboard showing:

- Latest GodScore
- Historical trend
- Commit-level history
- Explanation of score changes
- Enforcement context

The dashboard updates on every push via GitHub Actions.

https://willshacklett.github.io/godscore-ci/dashboard/

---

## Pricing

Free tier:
- Computes GodScore
- Prints guidance in CI logs
- Publishes dashboard and history
- Never blocks builds

Paid tier — $10/month per repo:
- Enables enforcement mode
- Can fail builds when trust drops too low
- Designed for governance, compliance, and policy use

Free informs. Paid enforces.

---

## Inputs

- score — Optional. GodScore to evaluate (0–1 or 0–100)
- threshold — Minimum acceptable score
- min_score — Alias for threshold
- mode — free (warn) or pro (fail)
- enforce — Explicit enforcement toggle
- pro_token — Reserved for future use

---

## Outputs

- godscore — Final normalized score (0–1)
- gv — Computed GV value (0–1)
- passed — Whether the gate passed
- effective_mode — Resolved mode
- score_source — manual or auto

---

## Design philosophy

- Honesty over green lights
- Trends matter more than snapshots
- Governance is about recovery, not punishment
- Survivability beats perfection

---

## Roadmap

- Expanded GV engine
- Component-level breakdowns
- Organization-wide dashboards
- Compliance exports
- Enterprise and safety integrations

---

## Author

William Shacklett

---

GodScore CI is not about stopping change.  
It’s about surviving it.
