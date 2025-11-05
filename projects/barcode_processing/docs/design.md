Barcode Processing — design notes

Goal
----
Small, interview-friendly helpers for extracting and correcting short barcodes from reads. Keep dependency-free and deterministic.

Components
----------
- `src/barcode/core.py`: extraction, simple Hamming-based correction, basic counting helpers.
- `tests/test_barcode.py`: smoke and basic validation tests.
- `bench_barcode.py`: small timing harness.

Tradeoffs
--------
Hamming-based correction is naive (O(|whitelist|)) but easy to explain; production systems use trie/bk-tree or bloom filter assisted correction.
