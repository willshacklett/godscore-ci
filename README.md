# GodScore CI

![CI](https://github.com/willshacklett/godscore-ci/actions/workflows/godscore-ci.yml/badge.svg)

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
