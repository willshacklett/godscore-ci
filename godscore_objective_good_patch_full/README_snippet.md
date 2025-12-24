![GodScore Moral CI](https://github.com/willshacklett/godscore-ci/actions/workflows/godscore-ci.yml/badge.svg)

## Objective Good Moral Field (God Variable)

This module encodes the moral potential \(\Phi_G\) and a decision helper that
augments ordinary rewards with a universal moral constant \(\kappa_G\).

**Files added**
- `docs/God_Variable_Objective_Good_Field_Spec.pdf` — one‑page spec
- `config/god_variable.json` — default constants (κ_G, weights, thresholds)
- `src/godscore/moral_field.py` — implementation (pure stdlib)
- `tests/test_moral_field.py` — invariants + example tests

**Run locally**
```bash
pip install -U pytest
pytest -q
```

**Use in code**
```python
from godscore.moral_field import choose_action, DEFAULT_CONFIG
# define model_eval_fn(state, action) -> dict as in docstring, then:
best, val = choose_action(state, candidates, model_eval_fn, DEFAULT_CONFIG)
```

## Objective Good Moral Field (κᴳ)

The God Variable module introduces an invariant moral constant κᴳ that anchors AI reasoning to an
objective moral axis (Good ↔ Evil, Hope ↔ Fear).

**Default configuration**
- κᴳ = 1.0  
- Weights: all = 1.0  
- Thresholds:  
  - Non-maleficence ≥ 0.5  
  - Autonomy ≥ 0.5  
  - Justice ≥ 0.5  
  - Truthfulness ≥ 0.6  

See [`docs/God_Variable_Objective_Good_Field_Spec.pdf`](docs/God_Variable_Objective_Good_Field_Spec.pdf) for the formal specification.
