UMI Dedup mini-project

How to run

Run tests:

```bash
pytest projects/umi_dedup/tests -q
```

Run the tiny benchmark:

```bash
python3 projects/umi_dedup/bench_umi.py
```

What this project contains

- `src/umi/core.py`: exact-match deduplication, Hamming-distance clustering, and consensus helpers.
- `tests/`: unit tests including clustering and consensus edge cases.
- `docs/design.md`: design decisions and tradeoffs.
- `bench_umi.py`: simple timing harness.

Notes
- Clustering is intentionally naive (quadratic) for clarity; replace with optimized or approximate methods for production.
