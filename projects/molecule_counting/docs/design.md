Molecule Counting — design notes

Goal
----
Provide a tiny, interview-friendly molecule counting utility that demonstrates grouping UMIs by gene and counting unique molecules.

Components
----------
- `src/molecule/core.py`: count_molecules, collapse_umis_by_count
- `tests/test_molecule.py`: smoke tests
- `bench_molecule.py`: small timing harness

Tradeoffs
--------
Exact-match grouping of UMIs is simple and deterministic. More realistic pipelines use clustering/UMI-correction and consensus approaches; those are left as extensions.
