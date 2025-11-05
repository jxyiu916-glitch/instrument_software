"""UMI clustering utilities.

This module provides clustering and distance functions used by the
deduplication pipeline. The clustering algorithm is a single-linkage
connected-components algorithm using Hamming distance, suitable for short
UMIs (length <= 16). It is implemented efficiently using pairwise
comparisons but could be swapped for BK-trees or locality-sensitive
hashing for very large datasets.
"""
from __future__ import annotations

from typing import List, Dict, Iterable, Tuple
from collections import defaultdict


def hamming_distance(a: str, b: str) -> int:
    """Return Hamming distance between equal-length strings.

    Raises ValueError for unequal lengths.
    """
    if len(a) != len(b):
        raise ValueError("Hamming distance requires equal-length strings")
    return sum(x != y for x, y in zip(a, b))


def cluster(umis: Iterable[str], max_distance: int = 1) -> Dict[str, List[str]]:
    """Cluster UMIs using single-linkage based on Hamming distance.

    Returns a dict mapping an arbitrary representative UMI to the list of
    UMIs in that cluster.
    """
    seqs = list(umis)
    n = len(seqs)
    if n == 0:
        return {}

    # Union-Find (Disjoint Set) implementation
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra = find(a)
        rb = find(b)
        if ra != rb:
            parent[rb] = ra

    # Naive pairwise comparison: O(n^2) but fine for typical UMI cluster sizes.
    for i in range(n):
        for j in range(i + 1, n):
            try:
                if hamming_distance(seqs[i], seqs[j]) <= max_distance:
                    union(i, j)
            except ValueError:
                # Skip comparison for unequal lengths
                continue

    clusters: Dict[int, List[str]] = defaultdict(list)
    for idx, s in enumerate(seqs):
        clusters[find(idx)].append(s)

    # Map representative -> cluster members
    result: Dict[str, List[str]] = {}
    for comp in clusters.values():
        rep = comp[0]
        result[rep] = comp
    return result

