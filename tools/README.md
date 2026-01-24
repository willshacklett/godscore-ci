# GV Tools – Constraint-Field Executables

- `gv_scoring_cli.py`: Core trajectory scorer. Detects margin loss acceleration, irreversibility precursors.
  Usage: `./gv_scoring_cli.py data.csv --threshold 0.82 --weights '{"safety":3.0}'`
- `gv_eval.py`: Evaluation harness (existing).
- `static_analysis.py` / `test_runner.py`: Legacy tool runners.

All tools zero-dependency beyond pandas/numpy/scipy.
