"""High-level molecule counting API.

This module provides a backwards-compatible surface for the tests and a
production-ready implementation that can later be extended to support cell
barcodes, consensus calling, and more sophisticated UMI-collapsing strategies.
"""
from typing import Iterable, Dict, Tuple, List

from .counter import count_molecules_from_pairs, collapse_umis_by_count_pairs
from .clustering import cluster_umis


RecordPair = Tuple[str, str]


def count_molecules(records: Iterable[RecordPair]) -> Dict[str, int]:
    """Count unique molecules per gene from iterable of (gene, umi) pairs.

    Backwards-compatible: each distinct (gene, umi) is counted as a single
    molecule regardless of read support.
    """
    return count_molecules_from_pairs(records)


def collapse_umis_by_count(records: Iterable[RecordPair], min_reads: int = 1) -> Dict[Tuple[str, str], int]:
    """Return (gene, umi) -> supporting_read_count filtered by min_reads.

    Keeps the legacy API used by tests but delegates to the clearer helper.
    """
    return collapse_umis_by_count_pairs(records, min_reads=min_reads)


def collapse_umis_by_distance(records: Iterable[RecordPair], max_distance: int = 1) -> Dict[Tuple[str, str], List[str]]:
    """Collapse UMIs per gene by clustering similar UMIs using Hamming distance.

    Returns a mapping (gene, representative_umi) -> list_of_member_umis.

    This function is useful when sequencing or synthesis errors produce
    near-duplicate UMIs that should be treated as the same molecule. It only
    clusters UMIs that are equal-length within each gene; UMIs of differing
    lengths are not compared.
    """
    # Group UMIs per gene
    per_gene: Dict[str, List[str]] = {}
    for gene, umi in records:
        per_gene.setdefault(gene, []).append(umi)

    out: Dict[Tuple[str, str], List[str]] = {}
    for gene, umis in per_gene.items():
        clusters = cluster_umis(umis, max_distance=max_distance)
        for rep, members in clusters.items():
            out[(gene, rep)] = members
    return out
