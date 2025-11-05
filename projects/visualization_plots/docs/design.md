Visualization & Diagnostics Plots — design notes

Goal
----
Provide small, interview-friendly plotting and diagnostics helpers that are useful for fleet/instrument monitoring and quick visual QA.

Components
----------
- `src/viz/core.py`: histogram bins, coverage plotting helpers, simple anomaly scoring and an ML model wrapper hook.
- `tests/test_viz.py`: smoke tests.
- `bench_viz.py`: tiny bench harness.

Tradeoffs
--------
- Keep plotting logic separated from plotting library calls to make testing easy and deterministic.
- Provide an ML integration hook as a thin wrapper; do not include heavy ML dependencies in the mini-project.
