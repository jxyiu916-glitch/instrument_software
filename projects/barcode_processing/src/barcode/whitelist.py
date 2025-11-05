"""Whitelist and counting helpers for barcodes."""

from typing import Iterable, Set, Dict, List, Tuple


def build_whitelist(barcodes: Iterable[str]) -> Set[str]:
    return set(barcodes)


def barcode_counts(barcodes: Iterable[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for b in barcodes:
        counts[b] = counts.get(b, 0) + 1
    return counts


def top_barcodes(counts: Dict[str, int], n: int = 10) -> List[Tuple[str, int]]:
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
