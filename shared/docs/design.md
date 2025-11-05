Design notes
============

This project is intentionally small and demonstrates:

- Clear separation of concerns: `src/app/core.py` contains the core logic.
- `src/cli.py` provides a small CLI for running the code with example data.
- `tests/` contains unit tests for core functionality.
- `data/` contains a tiny example dataset for deterministic runs.

If the real miniproject requires an HTTP API or persistent storage, add a small FastAPI server under `src/api/` and use an in-memory store or SQLite for persistence.
