Visualization & Diagnostics Plots mini-project

How to run

Run tests:

```bash
pytest projects/visualization_plots/tests -q
```

Run the tiny benchmark:

```bash
python3 projects/visualization_plots/bench_viz.py
```

Notes

- Plotting functions are designed to separate data computation from rendering so tests can run without matplotlib.
- ML integration is a thin wrapper; pass a `model_predict` callable to `ml_anomaly_wrapper` to get model-provided scores.
