"""Small script to run a tuner and save a step response plot."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from src.control.core import Plant, PID, tune_pid_grid, tune_pid_neldermead, simulate


def plot_response(t, y, title: str, out: Path):
    plt.figure(figsize=(6, 3))
    plt.plot(t, y, label="y")
    plt.axhline(1.0, color="k", linestyle="--", label="setpoint")
    plt.xlabel("time (s)")
    plt.ylabel("output")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out)
    print(f"Saved plot to {out}")


def main():
    plant = Plant(wn=1.0, zeta=0.2, K=1.0)
    print("Running grid tuner (coarse)...")
    best_g, metrics_g = tune_pid_grid(plant, kp_steps=6, ki_steps=4, kd_steps=3, t_final=4.0, dt=0.002)
    print("Grid metrics:", metrics_g)
    t, y, _ = simulate(plant, best_g, setpoint=1.0, t_final=4.0, dt=0.002)
    out_dir = Path("plots")
    out_dir.mkdir(exist_ok=True)
    plot_response(t, y, "Grid Tuner Response", out_dir / "grid_response.png")

    print("Running Nelder-Mead tuner...")
    best_nm, metrics_nm = tune_pid_neldermead(plant, t_final=4.0, dt=0.002, maxiter=100)
    print("NM metrics:", metrics_nm)
    t2, y2, _ = simulate(plant, best_nm, setpoint=1.0, t_final=4.0, dt=0.002)
    plot_response(t2, y2, "Nelder-Mead Response", out_dir / "nm_response.png")


if __name__ == "__main__":
    main()
