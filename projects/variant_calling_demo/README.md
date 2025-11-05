# Variant Calling Demo

Tiny educational SNP caller.

Usage (from repository root):

1. Run tests:

   pytest -q projects/variant_calling_demo/tests

2. Import and call:

   from variant.core import call_variants
   ref = "ACGTACGT"
   reads = [(0, "ACGT"), (2, "GTAA")]
   calls = call_variants(ref, reads)

This project is intentionally minimal and intended to be used as part of
the broader interview-style mini-project collection.
