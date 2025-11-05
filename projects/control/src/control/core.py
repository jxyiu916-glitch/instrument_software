from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List, Callable, Optional

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


def _score_pid(plant: Plant, pid: PID, setpoint: float, t_final: float, dt: float, settling_target: float) -> float:
    t, y, _ = simulate(plant, pid, setpoint, t_final=t_final, dt=dt)
    overshoot, settling = step_metrics(t, y, setpoint)
    score = overshoot + max(0.0, (settling - settling_target) / max(1.0, settling_target))
    score += 0.001 * (abs(pid.Kp) + abs(pid.Ki) + abs(pid.Kd))
    return score


def tune_pid_neldermead(plant: Plant,
                        setpoint: float = 1.0,
                        t_final: float = 5.0,
                        dt: float = 0.002,
                        x0: Optional[List[float]] = None,
                        maxiter: int = 200,
                        tol: float = 1e-3,
                        settling_target: float = 2.0) -> Tuple[PID, dict]:
    """Simple Nelder-Mead optimizer to tune PID gains.

    This lightweight implementation is interview-friendly and avoids external deps.
    It optimizes {Kp,Ki,Kd} starting from x0 (or a heuristic) to minimize the score.
    """
    # initial guess
    if x0 is None:
        x0 = [1.0, 0.1, 0.01]

    # Initialize simplex: x0 and small perturbations
    n = 3
    simplex = [list(x0)]
    scale = [max(1e-2, abs(v) * 0.1) for v in x0]
    for i in range(n):
        xi = list(x0)
        xi[i] += scale[i]
        simplex.append(xi)

    def eval_x(x: List[float]) -> float:
        pid = PID(x[0], x[1], x[2])
        return _score_pid(plant, pid, setpoint, t_final, dt, settling_target)

    # Evaluate simplex
    vals = [eval_x(x) for x in simplex]

    it = 0
    while it < maxiter:
        # order
        idx = sorted(range(len(simplex)), key=lambda i: vals[i])
        simplex = [simplex[i] for i in idx]
        vals = [vals[i] for i in idx]
        best_val = vals[0]
        worst_val = vals[-1]
        second_worst_val = vals[-2]

        # termination
        if max(abs(best_val - v) for v in vals) < tol:
            break

        # centroid of all but worst
        centroid = [0.0] * n
        for s in simplex[:-1]:
            for j in range(n):
                centroid[j] += s[j]
        for j in range(n):
            centroid[j] /= (len(simplex) - 1)

        # reflection
        alpha = 1.0
        xr = [centroid[j] + alpha * (centroid[j] - simplex[-1][j]) for j in range(n)]
        fr = eval_x(xr)
        if fr < best_val:
            # expansion
            gamma = 2.0
            xe = [centroid[j] + gamma * (xr[j] - centroid[j]) for j in range(n)]
            fe = eval_x(xe)
            if fe < fr:
                simplex[-1] = xe
                vals[-1] = fe
            else:
                simplex[-1] = xr
                vals[-1] = fr
        elif fr < second_worst_val:
            simplex[-1] = xr
            vals[-1] = fr
        else:
            # contraction
            rho = 0.5
            xc = [centroid[j] + rho * (simplex[-1][j] - centroid[j]) for j in range(n)]
            fc = eval_x(xc)
            if fc < vals[-1]:
                simplex[-1] = xc
                vals[-1] = fc
            else:
                # shrink
                sigma = 0.5
                for i in range(1, len(simplex)):
                    simplex[i] = [simplex[0][j] + sigma * (simplex[i][j] - simplex[0][j]) for j in range(n)]
                    vals[i] = eval_x(simplex[i])
        it += 1

    best = simplex[0]
    pid = PID(best[0], best[1], best[2])
    t, y, _ = simulate(plant, pid, setpoint, t_final=t_final, dt=dt)
    overshoot, settling = step_metrics(t, y, setpoint)
    metrics = {"Kp": pid.Kp, "Ki": pid.Ki, "Kd": pid.Kd, "overshoot": overshoot, "settling": settling, "score": _score_pid(plant, pid, setpoint, t_final, dt, settling_target), "iterations": it}
    return pid, metrics
