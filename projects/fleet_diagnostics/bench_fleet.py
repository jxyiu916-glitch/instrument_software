import time

from fleet.core import (
    detect_out_of_bounds,
    fleet_health_summary,
    compute_speeds,
    detect_speed_anomalies,
)


def bench():
    # create simple trajectories for 100 vehicles
    trajectories = []
    for v in range(100):
        traj = [(i, (v + i) % 10) for i in range(200)]
        trajectories.append(traj)

    bounds = (0, 500, 0, 10)
    t0 = time.time()
    # test out-of-bounds at a single timestamp
    _ = detect_out_of_bounds([(0, 0), (600, 0)], bounds)
    _ = fleet_health_summary([{"ok": True} for _ in range(100)])
    # compute speeds for first trajectory
    speeds = compute_speeds(trajectories[0], dt=0.5)
    _ = detect_speed_anomalies(speeds, speed_threshold=50.0)
    print("fleet bench done", time.time() - t0)


if __name__ == '__main__':
    bench()
