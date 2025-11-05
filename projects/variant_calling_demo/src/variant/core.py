"""Small variant calling demo (pileup-style SNP caller).

This is a tiny, deterministic, dependency-free implementation intended for
interview / educational use. It accepts a reference string and a list of
aligned reads represented as (start_pos, seq) pairs (0-based reference
coordinates). It produces simple SNP calls when an alternate base meets
minimum count and allele-fraction thresholds.

Contract:
- Inputs: ref: str, reads: Iterable[Tuple[int, str]]
- Outputs: List[dict] with keys: pos (0-based), ref, alt, depth, alt_count, af
- Errors: raises ValueError on out-of-range reference accesses
"""
from collections import defaultdict
from typing import Iterable, List, Dict, Tuple


def pileup_from_reads(reads: Iterable[Tuple[int, str]]) -> Dict[int, defaultdict]:
    """Build a simple pileup: mapping pos -> counts dict.

    reads: iterable of (start_pos, seq)
    returns: dict mapping 0-based reference position -> defaultdict(int) for base counts
    """
    pileup = {}
    for start, seq in reads:
        for i, b in enumerate(seq):
            pos = start + i
            if pos not in pileup:
                pileup[pos] = defaultdict(int)
            pileup[pos][b.upper()] += 1
    return pileup


def call_variants(
    ref: str,
    reads: Iterable[Tuple[int, str]],
    min_count: int = 2,
    min_af: float = 0.2,
) -> List[Dict]:
    """Call simple SNPs from reads against a short reference.

    For each reference position covered by reads, compute the most frequent
    alternate base and report a variant if alt_count >= min_count and
    alt_count/depth >= min_af.

    Note: This demo ignores indels, base qualities, mapping qualities and
    read pairing. It's intentionally minimal.
    """
    if min_af <= 0 or min_af > 1:
        raise ValueError("min_af must be in (0,1]")

    pileup = pileup_from_reads(reads)
    variants = []

    for pos, counts in sorted(pileup.items()):
        if pos < 0 or pos >= len(ref):
            raise ValueError(f"Pileup position {pos} out of reference range")
        ref_base = ref[pos].upper()
        total = sum(counts.values())
        if total == 0:
            continue
        # find top alt base (excluding reference base)
        alt_candidates = [(b, c) for b, c in counts.items() if b != ref_base]
        if not alt_candidates:
            continue
        alt_base, alt_count = max(alt_candidates, key=lambda x: x[1])
        af = alt_count / total
        if alt_count >= min_count and af >= min_af:
            variants.append(
                {
                    "pos": pos,
                    "ref": ref_base,
                    "alt": alt_base,
                    "depth": total,
                    "alt_count": alt_count,
                    "af": af,
                }
            )
    return variants


def pretty_print(variants: List[Dict]) -> str:
    """Return a compact multi-line string summarizing variant calls."""
    lines = []
    for v in variants:
        lines.append(
            f"pos={v['pos']} ref={v['ref']} alt={v['alt']} depth={v['depth']} alt_count={v['alt_count']} af={v['af']:.3f}"
        )
    return "\n".join(lines)
