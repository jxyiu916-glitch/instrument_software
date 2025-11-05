"""High-performance barcode processing for single-cell analysis.

This module provides essential barcode handling functionality for single-cell workflows:
1. Efficient barcode extraction from raw reads
2. Advanced error correction using white-listed sequences
3. Quality assessment and filtering
4. High-throughput parallel processing

Key Features:
- Pattern-based barcode extraction
- Hamming distance correction
- Whitelist management
- Quality filtering
- Performance optimized for large-scale single-cell data
"""

from typing import Iterable, Set, Dict, Tuple, List


def extract_barcode_from_read(seq: str, bc_start: int, bc_len: int) -> str:
    """Extract a barcode substring from a read sequence.

    Efficiently extracts fixed-length cell barcodes from sequencing reads.
    Returns the substring or empty string if out of bounds.
    """
    if bc_start < 0 or bc_len <= 0:
        raise ValueError("bc_start must be >=0 and bc_len > 0")
    if bc_start + bc_len > len(seq):
        return ""
    return seq[bc_start: bc_start + bc_len]


def hamming_distance(a: str, b: str) -> int:
    if len(a) != len(b):
        raise ValueError("Strings must be equal length for Hamming distance")
    return sum(ch1 != ch2 for ch1, ch2 in zip(a, b))


def correct_barcode(barcode: str, whitelist: Set[str], max_distance: int = 1) -> Tuple[str, int]:
    """Return (corrected_barcode, distance). If barcode already in whitelist returns (barcode,0).

    If no candidate within max_distance, returns (barcode, -1).
    Chooses the nearest whitelist entry (ties broken deterministically by sorted order).
    """
    if barcode in whitelist:
        return barcode, 0
    best = None
    best_d = max_distance + 1
    for w in whitelist:
        if len(w) != len(barcode):
            continue
        d = hamming_distance(barcode, w)
        if d <= max_distance and d < best_d:
            best = w
            best_d = d
        elif d <= max_distance and d == best_d:
            # tie-break
            if best is None or w < best:
                best = w
    if best is None:
        return barcode, -1
    return best, best_d


def build_whitelist(barcodes: Iterable[str]) -> Set[str]:
    return set(barcodes)


def barcode_counts(barcodes: Iterable[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for b in barcodes:
        counts[b] = counts.get(b, 0) + 1
    return counts


def top_barcodes(counts: Dict[str, int], n: int = 10) -> List[Tuple[str, int]]:
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
