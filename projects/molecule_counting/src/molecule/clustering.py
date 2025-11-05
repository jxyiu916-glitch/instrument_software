"""UMI clustering utilities.

Production-ready helpers to cluster UMIs by Hamming distance using a union-find
single-linkage approach. This implementation is intentionally simple and
deterministic (pairwise comparisons) which is appropriate for typical per-gene
UMI sets (usually small). For extremely large sets, a BK-tree or locality
sensitive hashing would be recommended.
"""
from typing import List, Dict, Tuple


def hamming_distance(a: str, b: str) -> int:
    """Return the Hamming distance between equal-length strings.

    Raises ValueError if lengths differ.
    """
    if len(a) != len(b):
        raise ValueError("hamming_distance requires equal-length strings")
    return sum(x != y for x, y in zip(a, b))


class _UnionFind:
    def __init__(self, items: List[str]):
        self.parent = {i: i for i in range(len(items))}
        self.items = items

    def find(self, i: int) -> int:
        if self.parent[i] != i:
            self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: int, j: int) -> None:
        ri, rj = self.find(i), self.find(j)
        if ri != rj:
            self.parent[rj] = ri


def cluster_umis(umis: List[str], max_distance: int = 1) -> Dict[str, List[str]]:
    """Cluster UMIs by single-linkage using Hamming distance.

    Returns a mapping representative_umi -> list_of_umis_in_cluster. The
    representative is the first UMI encountered that belongs to the cluster.
    """
    if not umis:
        return {}

    # Deduplicate input order-preserving
    seen: Dict[str, int] = {}
    unique: List[str] = []
    for u in umis:
        if u not in seen:
            seen[u] = len(unique)
            unique.append(u)

    uf = _UnionFind(unique)
    n = len(unique)
    for i in range(n):
        for j in range(i + 1, n):
            try:
                d = hamming_distance(unique[i], unique[j])
            except ValueError:
                # differing lengths -> skip clustering between these UMIs
                continue
            if d <= max_distance:
                uf.union(i, j)

    clusters: Dict[int, List[str]] = {}
    for idx, umi in enumerate(unique):
        root = uf.find(idx)
        clusters.setdefault(root, []).append(umi)

    # Convert to representative -> members, pick representative by lowest index
    result: Dict[str, List[str]] = {}
    for root_idx, members in clusters.items():
        rep = unique[root_idx]
        result[rep] = members
    return result

