Control mini-project design notes
===============================

Goal
----
Implement a small control-loop simulator (2nd-order plant) and a PID controller with two tuning approaches:
1. Simple grid search (interview-friendly)
2. Nelder-Mead optimization (more efficient)

Design choices
--------------
- Plant: represented as a second-order mass-spring-damper ODE discretized using forward Euler for simplicity and deterministic reproducibility.
- Controller: classic PID with anti-windup via integrator clamping.
- Tuners: 
  1. Grid search: deterministic scan of the gain space, simple but slow
  2. Nelder-Mead: derivative-free optimization that usually finds better gains faster

Deliverables
------------
- `src/control/core.py`: Plant, PID, simulate(), step_metrics(), tune_pid_grid(), tune_pid_neldermead()
- `tests/test_control.py`: smoke tests and tuner validation tests
- `scripts/plot_tuning.py`: visualizes step responses for both tuners
- `scripts/bench_control.py`: compares tuner performance
- `docs/control_design.md`: short design note (this file)
- `cpp/README.md`: notes on C++ port (future)

Tradeoffs
---------
- Euler integration is simple but can be inaccurate for stiff systems; use smaller dt for stability.
- Grid search is brute-force but deterministic; replace with Bayesian optimization or analytic tuning (Ziegler–Nichols) for speed.

Next steps (if extending)
-------------------------
- Complete the C++ implementation (sketched in cpp/) for performance-critical components.
- Add CI benchmarks to check performance regression.
- Add Bode plot visualization to understand frequency response.
- Consider model-based tuning methods (pole placement, Ziegler-Nichols).
