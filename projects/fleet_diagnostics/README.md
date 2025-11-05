Fleet Diagnostics mini-project

How to run

Run tests:

```bash
pytest projects/fleet_diagnostics/tests -q
```

Run the tiny benchmark:

```bash
python3 projects/fleet_diagnostics/bench_fleet.py
```

What this project contains

- `src/fleet/core.py`: functions for bounds checks, health summaries, speed computations, and anomaly detection.
- `tests/`: unit and smoke tests including edge cases.
- `docs/design.md`: design decisions and tradeoffs.
- `bench_fleet.py`: simple timing harness.

Notes
- Tests insert the `src/` directory on `sys.path` so they run without needing an install step. This mirrors the repository's pattern for interview-friendly demo projects.
