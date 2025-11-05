"""Benchmark grid vs Nelder-Mead tuner runtimes."""
import time
from src.control.core import Plant, tune_pid_grid, tune_pid_neldermead


def bench():
    plant = Plant(wn=1.0, zeta=0.2, K=1.0)
    t0 = time.time()
    _ = tune_pid_grid(plant, kp_steps=6, ki_steps=4, kd_steps=3, t_final=3.0, dt=0.002)
    gtime = time.time() - t0
    t0 = time.time()
    _ = tune_pid_neldermead(plant, t_final=3.0, dt=0.002, maxiter=80)
    nmtime = time.time() - t0
    print(f"Grid tuner time: {gtime:.3f}s")
    print(f"Nelder-Mead time: {nmtime:.3f}s")


if __name__ == "__main__":
    bench()
