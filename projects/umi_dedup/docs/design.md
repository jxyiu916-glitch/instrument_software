UMI deduplication — design notes

Goal
----
Provide a tiny, interview-friendly UMI deduplication utility focusing on exact-match deduplication and simple summary statistics.

Components
----------
- `src/umi/core.py`: exact-match deduplication and simple metrics.
- `tests/test_umi.py`: smoke tests.
- `bench_umi.py`: small timing harness.

Tradeoffs
--------
Exact matching keeps the code simple; in practice, edit-distance or clustering-based approaches are often used.

Extensions added for "full parity":

- `hamming_distance(a,b)`: helper for equal-length UMIs.
- `cluster_umis(umi_list, max_distance)`: naive single-linkage clustering using Hamming distances (O(n^2)).
- `dedup_umis_clustered(...)`: wrapper to produce clustered counts.
- `umi_consensus(cluster_members)`: simple position-wise majority consensus.

Rationale: these additions demonstrate the typical next steps when moving from exact-match deduplication to realistic pipelines without pulling in heavy dependencies. The implementation is intentionally naive but clear for interview discussion.
