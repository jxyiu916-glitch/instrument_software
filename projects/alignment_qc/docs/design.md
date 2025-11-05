Alignment QC — design notes

Goal
----
Small helpers to summarize alignment files: mapping rate, soft-clipping statistics, insert-size summaries, and flag breakdowns. Designed for interview settings with deterministic, dependency-free code.

Components
----------
- `src/alignment/core.py`: mapping_rate, softclip_stats, insert_size_stats, flag_summary
- `tests/test_alignment.py`: smoke tests and edge cases
- `bench_alignment.py`: small timing harness

Tradeoffs
--------
Avoid full SAM/BAM parsing for clarity; these helpers accept lightweight records (dicts or tuples) to demonstrate how to compute common QC metrics.
