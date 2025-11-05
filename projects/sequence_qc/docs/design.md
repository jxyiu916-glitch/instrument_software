Sequence QC — design notes

Goal
----
Provide a tiny utility that computes basic per-read QC metrics suitable for interview problems: average read length and fraction of reads containing ambiguous base 'N'.

Components
----------
- `src/seqqc/core.py`: basic_qc_stats
- `tests/test_seqqc.py`: smoke tests
- `bench_seqqc.py`: tiny benchmark driver

Extensions added for "full parity":

- `gc_content(seqs)`: overall GC fraction across reads.
- `length_histogram(seqs)`: simple read-length histogram.
- `filter_by_length(seqs, min_len, max_len)`: trimming/filtering convenience helper.
- `per_base_n_fraction(seqs)`: per-position fraction of 'N' bases across reads.
- `simple_adapter_detection(seqs, adapter)`: heuristic adapter substring counting.

Rationale: these helpers are small, deterministic, and useful in interview problems to demonstrate string processing, simple statistics and input validation without pulling in heavy bioinformatics deps.
