Alignment QC mini-project

How to run

Run tests:

```bash
pytest projects/alignment_qc/tests -q
```

Run the tiny benchmark:

```bash
python3 projects/alignment_qc/bench_alignment.py
```

What this project contains

- `src/alignment/core.py`: helpers for mapping rate, soft-clip stats, insert-size stats and flag summaries.
- `tests/`: unit and smoke tests.
- `bench_alignment.py`: simple timing harness.

Notes

- The helpers operate on small, lightweight record dicts or tuples and are intentionally dependency-free for interview clarity.
