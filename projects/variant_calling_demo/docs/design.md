# Variant Calling Demo - Design

This mini-project is a compact, dependency-free demonstration of a simple
pileup-based single-nucleotide polymorphism (SNP) caller. It is intended
for interview/exercise use and illustrates the following:

- Building a pileup from aligned reads.
- Simple heuristics for calling SNPs (min count + allele fraction).
- Clear, testable contract and deterministic behavior.

Files:

- `src/variant/core.py` - implementation (pileup, caller, pretty printer).
- `tests/test_variant.py` - unit tests covering basic positive/negative cases.
- `bench_variant.py` - small harness to profile caller on synthetic data.

Design notes / tradeoffs:

- No base or mapping qualities are used; this keeps the implementation
  readable. In production, variant callers incorporate base qualities,
  read filters, indel handling, and local realignment.
- The API accepts reads as (start_pos, seq) tuples to avoid introducing
  complex SAM/BAM parsing dependencies.
- Extensibility: a C++ reimplementation can reuse the same API contract
  (pileup builder + per-position caller) and provide pybind11 bindings.

Next steps (optional):

- Add a minimal parser for a compact, text-based alignment format (for
  easier example inputs).
- Add unit tests for edge cases (reads extending off the reference,
  mixed-case bases, unexpected characters).
