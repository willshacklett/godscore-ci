# GodScore CI

## Irreversibility & Emergent Alignment Demo

This repository includes a deterministic demonstration showing that
optimization under a God Variable (Gv) penalty naturally avoids
irreversible actions that collapse future option space.

### What this shows
Without encoding ethics, values, or rules, a planning agent optimized
under Gv prefers:
- reversible actions
- corrigible strategies
- long-horizon survivability

over short-term destructive gains.

### How it works
- A toy environment defines **irreversibility** as permanent loss of future options
- A finite-horizon value iteration planner includes a Gv penalty
- Tests verify:
  - correct detection of irreversible actions
  - a policy shift away from irreversible shortcuts

### Run the demo

```bash
python experiments/exp_irreversibility_vi.py


GodScore CI is an experimental continuous-integration framework for evaluating
systems not only on correctness and performance, but on **long-term coherence,
auditability, and harm avoidance**.

## Core Idea

GodScore introduces a scoring layer intended to penalize:
- irreversible harm,
- suppression of correction or dissent,
- moral certainty without falsifiability,
- optimization paths that collapse long-term system survivability.

The goal is not to define truth, ideology, or authority, but to preserve the
conditions under which intelligent systems can continue to correct themselves.

## Non-Claim

This project does **not** assert moral superiority, religious authority, or
political alignment. Any use of GodScore to justify coercion, irreversibility,
or centralized power contradicts its purpose.

## Status

This repository currently focuses on CI workflows and test scaffolding.
The objective logic and scoring mechanisms are intentionally modular and auditable.

## Toy Survivability Experiment (Falsifiable Demonstration)

This repository includes a minimal, non-physical toy model demonstrating a
selection principle underlying the God Variable (Gv).

In the experiment, simple systems are subjected to repeated stochastic
perturbations. Systems with higher Gv proxy scores—reflecting robustness,
coherence, adaptability, and error correction—statistically outlive more
fragile systems on average.

This experiment is intentionally simple and makes no claim to model physical
reality. Its purpose is to demonstrate a falsifiable selection effect under
perturbation, not to explain the origin of the universe.

To visualize the relationship between Gv score and survival time, run:
`python scripts/plot_gv_survival.py`

See:
- `godscore_ci/toy_sim.py`
- `tests/test_toy_survival.py`

An ablation test further shows that removing error correction causes a substantial collapse in survivability, even when other factors are held constant.
