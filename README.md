# Interview Mini-Project Template

This repository is a minimal, interview-style project scaffold designed for practice and timed miniprojects.

Goals:
- Small, well-scoped code under `src/` with a CLI entrypoint.
- Unit tests under `tests/` and a small example dataset under `data/`.
- Optional Dockerfile, GitHub Actions CI, and a benchmarking script.

Quick start (macOS / zsh):

```bash
# create virtualenv and activate
python3 -m venv .venv
source .venv/bin/activate

# install dev dependencies
pip install -r requirements.txt

# run tests
pytest -q

# run example
python -m src.cli data/example_small.json
```

If you want additional scaffolding (HTTP API, React UI, or more advanced benchmarks), answer the follow-up questions and I will add them.