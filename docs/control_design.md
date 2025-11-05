Control mini-project design notes
===============================

Goal
----
Implement a small control-loop simulator (2nd-order plant) and a PID controller with a simple tuner.

Design choices
--------------
- Plant: represented as a second-order mass-spring-damper ODE discretized using forward Euler for simplicity and deterministic reproducibility.
- Controller: classic PID with anti-windup via integrator clamping.
- Tuner: deterministic grid search to find a candidate set of gains that meet soft performance targets. Grid search is simple and interview-friendly; in production you'd use model-based tuning or optimization.

Deliverables
------------
- `src/control/core.py`: Plant, PID, simulate(), step_metrics(), tune_pid_grid()
- `tests/test_control.py`: smoke tests and a tuner validation test
- `docs/control_design.md`: short design note (this file)

Tradeoffs
---------
- Euler integration is simple but can be inaccurate for stiff systems; use smaller dt for stability.
- Grid search is brute-force but deterministic; replace with Bayesian optimization or analytic tuning (Ziegler–Nichols) for speed.

Next steps (if extending)
-------------------------
- Provide a C++ implementation of the Plant and PID for performance-critical components.
- Add CI benchmarks to check performance regression.
- Add visualization (notebook) for step responses and Bode plots.
