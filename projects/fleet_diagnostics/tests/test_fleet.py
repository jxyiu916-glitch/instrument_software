import os
import sys

# make project src visible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from fleet.core import (
    detect_out_of_bounds,
    fleet_health_summary,
    compute_speeds,
    detect_speed_anomalies,
    aggregate_missing_gps,
)


def test_detect_out_of_bounds_basic():
    positions = [(0, 0), (5, 5), (10, 10), (-1, 0)]
    bounds = (0, 10, 0, 10)
    out = detect_out_of_bounds(positions, bounds)
    assert set(out) == {3}


def test_fleet_health_summary():
    flags = [{"ok": True}, {"ok": False}, {"ok": True}]
    s = fleet_health_summary(flags)
    assert s["total"] == 3
    assert s["ok"] == 2
    assert s["faults"] == 1


def test_compute_speeds_and_anomalies():
    # positions: 3 samples, first move 1 unit, then jump 10 units
    positions = [(0, 0), (1, 0), (11, 0)]
    speeds = compute_speeds(positions, dt=1.0)
    assert len(speeds) == 2
    assert abs(speeds[0] - 1.0) < 1e-6
    assert abs(speeds[1] - 10.0) < 1e-6
    anoms = detect_speed_anomalies(speeds, speed_threshold=5.0)
    assert anoms == [1]


def test_aggregate_missing_gps():
    flags = [{"gps_ok": True}, {"gps_ok": False}, {}]
    assert aggregate_missing_gps(flags) == 1


def test_compute_speeds_invalid_dt():
    positions = [(0, 0), (1, 1)]
    import pytest

    with pytest.raises(ValueError):
        compute_speeds(positions, dt=0)
