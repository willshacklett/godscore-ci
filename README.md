# GodScore CI
**Survivability-Aware Continuous Integration (CI)**

GodScore CI is a GitHub Action + CI gate that enforces a survivability threshold during builds.

Most CI systems answer:
- “Does it compile?”
- “Do tests pass?”
- “Is performance acceptable?”

GodScore CI adds a different gate:

> “Does this change reduce long-term survivability?”

If survivability falls below a policy threshold, the build fails.

---

## Why this exists

Traditional CI is great at correctness and speed, but it does not reliably catch:
- irreversible optimization paths
- long-term risk accumulation
- short-term gains that reduce system survivability

GodScore CI introduces an **enforceable contract** upstream of deployment:
- configurable policy threshold
- deterministic enforcement
- audit trail (per-run history)

---

## Quick Start (GitHub Actions)

Add this to a workflow step:

```yaml
- uses: willshacklett/godscore-ci@v1
  with:
    score: 0.82
    threshold: 0.80


