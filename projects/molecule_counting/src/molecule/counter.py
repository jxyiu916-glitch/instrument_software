"""Molecule counting helpers.

Lightweight, well-typed utilities used by the higher-level `core` functions.
These helpers are intentionally dependency-free and easy to test.
"""
from typing import Iterable, Dict, Tuple, Iterable, List


def _group_counts(keys: Iterable[Tuple[str, str]]) -> Dict[Tuple[str, str], int]:
    """Count occurrences of (gene, umi) tuples.

    Returns a mapping (gene, umi) -> supporting_read_count.
    """
    counts: Dict[Tuple[str, str], int] = {}
    for key in keys:
        counts[key] = counts.get(key, 0) + 1
    return counts


def count_molecules_from_pairs(pairs: Iterable[Tuple[str, str]]) -> Dict[str, int]:
    """Return per-gene unique molecule counts given iterable of (gene, umi) pairs.

    This function treats each distinct (gene, umi) pair as a single molecule
    regardless of how many reads support it.
    """
    counts = _group_counts(pairs)
    per_gene: Dict[str, int] = {}
    for (gene, umi) in counts.keys():
        per_gene[gene] = per_gene.get(gene, 0) + 1
    return per_gene


def collapse_umis_by_count_pairs(pairs: Iterable[Tuple[str, str]], min_reads: int = 1) -> Dict[Tuple[str, str], int]:
    """Return (gene, umi) -> supporting_read_count only for UMIs with at least min_reads.

    This keeps the old behaviour used in tests while providing a clearer name
    for internal use.
    """
    counts = _group_counts(pairs)
    return {k: v for k, v in counts.items() if v >= min_reads}

