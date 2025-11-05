from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List

import math
import numpy as np


@dataclass
class Plant:
    """A simple second-order plant (mass-spring-damper style) simulated via Euler integration.

    x'' + 2*zeta*wn*x' + wn**2 * x = K * u
    """

    wn: float = 1.0  # natural frequency
    zeta: float = 0.2  # damping ratio
    K: float = 1.0  # plant gain

    def step(self, state: Tuple[float, float], u: float, dt: float) -> Tuple[float, float]:
        x, xdot = state
        # xdd = K*u - 2*zeta*wn*xdot - wn**2 * x
        xdd = self.K * u - 2.0 * self.zeta * self.wn * xdot - (self.wn ** 2) * x
        xdot_new = xdot + xdd * dt
        x_new = x + xdot_new * dt
        return x_new, xdot_new


@dataclass
class PID:
    Kp: float
    Ki: float
    Kd: float
    integrator_limit: float = 1e6

    def __post_init__(self):
        self.integral = 0.0
        self.last_error = 0.0

    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0

    def control(self, error: float, dt: float) -> float:
        self.integral += error * dt
        # anti-windup
        self.integral = max(min(self.integral, self.integrator_limit), -self.integrator_limit)
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        self.last_error = error
        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative


def simulate(plant: Plant, controller: PID, setpoint: float, t_final: float = 5.0, dt: float = 0.001) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simulate closed-loop response to a step setpoint.

    Returns (t, y, u)
    """
    steps = int(math.ceil(t_final / dt))
    t = np.linspace(0.0, t_final, steps)
    y = np.zeros(steps)
    u = np.zeros(steps)
    x, xdot = 0.0, 0.0
    controller.reset()
    for i in range(steps):
        error = setpoint - x
        u_i = controller.control(error, dt)
        # clamp control to reasonable range for numerical stability
        u_i = float(max(min(u_i, 1e3), -1e3))
        x, xdot = plant.step((x, xdot), u_i, dt)
        y[i] = x
        u[i] = u_i
    return t, y, u


def step_metrics(t: np.ndarray, y: np.ndarray, setpoint: float, settling_threshold: float = 0.02) -> Tuple[float, float]:
    """Compute overshoot (as fraction) and settling time (seconds).

    Overshoot: (max(y) - setpoint) / setpoint
    Settling time: first time after which |y-setpoint| <= settling_threshold*|setpoint|
    """
    if setpoint == 0:
        return 0.0, float('inf')
    overshoot = (np.max(y) - setpoint) / abs(setpoint)
    within = np.abs(y - setpoint) <= settling_threshold * abs(setpoint)
    # find first index after which all remaining samples are within threshold
    settling_time = float('inf')
    for i in range(len(within)):
        if all(within[i:]):
            settling_time = float(t[i])
            break
    return float(overshoot), settling_time


def tune_pid_grid(plant: Plant, setpoint: float = 1.0, t_final: float = 5.0, dt: float = 0.001,
                  kp_range=(0.1, 50.0), ki_range=(0.0, 50.0), kd_range=(0.0, 5.0),
                  kp_steps=5, ki_steps=5, kd_steps=3,
                  overshoot_target=0.2, settling_target=2.0) -> Tuple[PID, dict]:
    """A simple grid-search tuner. Returns best PID and metrics dict.

    This is intentionally simple and deterministic for interview practice.
    """
    best = None
    best_score = float('inf')
    best_metrics = {}
    kp_values = np.linspace(kp_range[0], kp_range[1], kp_steps)
    ki_values = np.linspace(ki_range[0], ki_range[1], ki_steps)
    kd_values = np.linspace(kd_range[0], kd_range[1], kd_steps)
    for Kp in kp_values:
        for Ki in ki_values:
            for Kd in kd_values:
                pid = PID(Kp, Ki, Kd)
                t, y, _ = simulate(plant, pid, setpoint, t_final=t_final, dt=dt)
                overshoot, settling = step_metrics(t, y, setpoint)
                # score: combine overshoot and settling; penalize if doesn't meet targets
                score = overshoot + max(0.0, (settling - settling_target) / max(1.0, settling_target))
                # small penalty for large control action (roughly)
                score += 0.001 * (abs(Kp) + abs(Ki) + abs(Kd))
                if score < best_score and overshoot <= 5.0:
                    best_score = score
                    best = pid
                    best_metrics = {"Kp": Kp, "Ki": Ki, "Kd": Kd, "overshoot": overshoot, "settling": settling, "score": score}
    return best, best_metrics
