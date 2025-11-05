from typing import List, Dict, Tuple
import math


def detect_out_of_bounds(positions: List[Tuple[float, float]], bounds: Tuple[float, float, float, float]) -> List[int]:
    """Return indices of vehicles whose (x,y) positions are outside the axis-aligned rectangular bounds.

    bounds = (xmin, xmax, ymin, ymax)
    positions: list of (x,y) for a single timestamp or for multiple vehicles at one instant.
    """
    xmin, xmax, ymin, ymax = bounds
    out = []
    for i, (x, y) in enumerate(positions):
        if x < xmin or x > xmax or y < ymin or y > ymax:
            out.append(i)
    return out


def fleet_health_summary(status_flags: List[Dict[str, bool]]) -> Dict[str, int]:
    """Compute simple summary counts for a list of per-vehicle status flags.

    Example status_flags element: {"ok": True, "sensor_fault": False}
    Returns counts: total, ok, faults, sensor_faults
    """
    summary = {"total": len(status_flags), "ok": 0, "faults": 0, "sensor_faults": 0}
    for s in status_flags:
        if s.get("ok", False):
            summary["ok"] += 1
        else:
            summary["faults"] += 1
        if s.get("sensor_fault", False):
            summary["sensor_faults"] += 1
    return summary


def compute_speeds(positions: List[Tuple[float, float]], dt: float) -> List[float]:
    """Compute instantaneous speeds between successive (x,y) positions.

    positions: list of (x,y) sampled at constant interval dt (seconds).
    Returns list of speeds (len = max(0, len(positions)-1)).
    Raises ValueError if dt <= 0.
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    if len(positions) < 2:
        return []
    speeds: List[float] = []
    for (x0, y0), (x1, y1) in zip(positions[:-1], positions[1:]):
        dx = x1 - x0
        dy = y1 - y0
        dist = math.hypot(dx, dy)
        speeds.append(dist / dt)
    return speeds


def detect_speed_anomalies(speeds: List[float], speed_threshold: float) -> List[int]:
    """Return indices where speed exceeds speed_threshold.

    Indices correspond to the speed list (i.e., between position i and i+1).
    """
    out = []
    for i, s in enumerate(speeds):
        if s > speed_threshold:
            out.append(i)
    return out


def aggregate_missing_gps(status_flags: List[Dict[str, bool]]) -> int:
    """Count vehicles reporting missing GPS (status flag 'gps_ok' == False)."""
    return sum(1 for s in status_flags if not s.get("gps_ok", True))


def simple_anomaly_detector(positions_over_time: List[List[Tuple[float, float]]], dt: float, speed_threshold: float) -> Dict[str, int]:
    """Run a tiny anomaly detection pass over multiple vehicle trajectories.

    positions_over_time: list of trajectories; each trajectory is a list of (x,y) sampled at interval dt.
    Returns summary: {"n_trajs", "n_speed_anoms", "n_missing_gps"}
    """
    n_trajs = len(positions_over_time)
    n_speed_anoms = 0
    for traj in positions_over_time:
        speeds = compute_speeds(traj, dt)
        n_speed_anoms += len(detect_speed_anomalies(speeds, speed_threshold))
    return {"n_trajs": n_trajs, "n_speed_anoms": n_speed_anoms}
