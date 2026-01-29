# GodScore CI

A survivability-aware CI gate that flags risky change early — and can **block merges** when enforcement is enabled.

## What it does
- Computes a **GodScore** for a change (you provide the score)
- Compares it to a **threshold**
- Runs in CI on every push / PR
- Writes a clean GitHub Actions step summary
- Optionally tracks recent successful runs for regression awareness

## Free vs Paid
**Free (advisory):**
- Prints warnings and guidance
- **Never fails your build**

**Paid ($10/month per repo) — Enforcement:**
- Enables **build blocking**
- Fails CI when `godscore < threshold`
- Makes risk non-optional

> Free informs. Paid enforces.

## Quick example

### Free (warn-only)
```yaml
- name: GodScore CI (Free)
  uses: willshacklett/godscore-ci@v0.2.4
  with:
    score: "0.85"
    threshold: "0.80"
    enforce: "false"
