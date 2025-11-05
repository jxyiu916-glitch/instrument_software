from src.control.core import Plant, PID, simulate, tune_pid_grid, step_metrics
import numpy as np


def test_plant_step_basic():
    plant = Plant(wn=1.0, zeta=0.1, K=1.0)
    pid = PID(2.0, 0.5, 0.01)
    t, y, u = simulate(plant, pid, setpoint=1.0, t_final=2.0, dt=0.001)
    # final value should be finite and close-ish to setpoint (this is a smoke test)
    assert np.isfinite(y[-1])


def test_tuner_finds_solution():
    plant = Plant(wn=1.0, zeta=0.2, K=1.0)
    best_pid, metrics = tune_pid_grid(plant, setpoint=1.0, t_final=5.0, dt=0.002,
                                     kp_range=(0.5, 20.0), ki_range=(0.0, 20.0), kd_range=(0.0, 2.0),
                                     kp_steps=6, ki_steps=4, kd_steps=3,
                                     overshoot_target=0.3, settling_target=2.0)
    assert best_pid is not None
    assert "overshoot" in metrics and "settling" in metrics
    # require reasonable overshoot and settling (not strict for grid search)
    assert metrics["overshoot"] < 1.0
    assert metrics["settling"] < 5.0


def test_step_metrics():
    t = np.linspace(0, 1, 101)
    y = np.linspace(0, 1, 101)
    overshoot, settling = step_metrics(t, y, setpoint=1.0, settling_threshold=0.02)
    assert overshoot == 0.0
    assert settling <= 1.0
