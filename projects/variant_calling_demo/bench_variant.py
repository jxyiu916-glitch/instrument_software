"""Small bench harness for the variant caller.

Generates synthetic reads with a configurable SNP frequency and times the caller.
"""
import random
import time

from variant.core import call_variants


def generate_reads(ref, depth=20, snp_pos=None, snp_af=0.2):
    reads = []
    L = len(ref)
    for _ in range(depth):
        start = 0
        seq = list(ref)
        if snp_pos is not None and random.random() < snp_af:
            # introduce an alternate at snp_pos
            refb = seq[snp_pos]
            alt = random.choice([b for b in "ACGT" if b != refb])
            seq[snp_pos] = alt
        reads.append((start, "".join(seq)))
    return reads


def main():
    ref = "A" * 100
    reads = generate_reads(ref, depth=1000, snp_pos=50, snp_af=0.3)
    t0 = time.time()
    calls = call_variants(ref, reads, min_count=5, min_af=0.1)
    dt = time.time() - t0
    print(f"Found {len(calls)} calls in {dt:.3f}s")


if __name__ == "__main__":
    main()
