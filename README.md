# GodScore CI

**GodScore CI prevents long-term system degradation by enforcing survivability and regression gates in continuous integration.**

**Survivability-Aware Continuous Integration Gate**

GodScore CI is a GitHub Action that adds a new kind of CI gate:

**long-term system survivability**.

Traditional CI answers:
- Does it compile?
- Do tests pass?
- Is performance acceptable?

GodScore CI asks a harder question:
> **Does this change reduce the system’s ability to survive, self-correct, or recover over time?**

If survivability drops below policy, the build fails.

---

## 🚦 What GodScore CI Enforces

GodScore CI evaluates a single scalar metric — the **God Variable (Gv)** — representing survivability, corrigibility, and irreversibility risk.

The gate fails if:

---

## 🔓 Free vs 🔒 Pro Modes

GodScore CI supports two execution modes designed to balance accessibility with enforcement.

### Free Mode (Default)
Free mode is designed for visibility and experimentation.

- Evaluates the God Variable (Gv) score
- Records survivability history (`gv_runs.json`)
- Detects survivability regression
- **Emits warnings only** on regression
- CI **does not fail** on regression alone

Free mode answers:
> “Is survivability trending in the wrong direction?”

### Pro Mode (Enforcement)
Pro mode is designed for policy enforcement in production CI.

- Requires a valid `GV_PRO_TOKEN`
- Enforces survivability thresholds
- Enforces **regression limits**
- **Fails CI** on survivability regression beyond policy
- Prevents silent long-term degradation

Pro mode answers:
> “Should this change be allowed to ship?”

---

## 📉 Survivability Regression Policy

GodScore CI does not only evaluate absolute survivability — it also detects **negative trends over time**.

A regression occurs when the current God Variable (Gv) score drops significantly below recent historical performance.

### Regression Handling by Mode

| Mode | Regression Detected | CI Result |
|-----|--------------------|-----------|
| Free | Yes | ⚠️ Warning only |
| Pro | Yes | ❌ Build fails |

This design allows teams to *see* survivability decay early, while reserving enforcement for production pipelines.

---

### Example: Free Mode (Warn Only)

```yaml
- uses: willshacklett/godscore-ci@v1
  with:
    score: 0.81
