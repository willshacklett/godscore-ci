# Governance (Exploratory)

This directory contains **non-functional, exploratory documentation** and examples
for evaluating **system-level changes** (e.g., product, policy, monetization, model
behavior) against long-term survivability constraints using a survivability scalar
(**Gv**).

Nothing in this directory affects GodScore CI runtime behavior unless explicitly
wired in by a user. The intent is to document a survivability-first way of thinking
about irreversible change.

## Contents

### Memos
- `memos/survivability_first_monetization.md`  
  Internal-style memo describing survivability-bounded monetization using Gv.

### Examples
Examples are **hypothetical** and provided to illustrate how survivability evaluation
could be structured.

- `examples/monetization_change.json`  
  Example survivability evaluation for a monetization experiment.

## Notes

- The numeric values in examples are placeholders meant to demonstrate structure.
- Gv is treated here as a **constraint framework** (survivability-first), not an ideology.
- This directory is intentionally calm and minimal: it’s meant to be legible to engineers,
  governance teams, and reviewers without requiring buy-in.
