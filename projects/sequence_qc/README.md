Sequence QC mini-project

How to run

Run tests:

```bash
pytest projects/sequence_qc/tests -q
```

Run the tiny benchmark:

```bash
python3 projects/sequence_qc/bench_seqqc.py
```

What this project contains

- `src/seqqc/core.py`: basic QC and string-processing helpers (average length, N-fractions, GC content, histograms, filters, adapter detection).
- `tests/`: unit tests including edge cases and validation.
- `docs/design.md`: design decisions and tradeoffs.
- `bench_seqqc.py`: simple timing harness.

Notes
- Helpers are designed to be small and dependency-free; they are intentionally simple for interview clarity. Add optimized or domain-specific libraries when moving to production.
