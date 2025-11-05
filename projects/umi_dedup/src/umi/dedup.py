"""UMI deduplication utilities.

This module implements robust UMI deduplication strategies suitable for
production use. Two principal algorithms are provided:

- collapse_directional: directional adjacency collapse (similar to UMI-tools),
  which collapses low-count UMIs into higher-count neighbours within edit
  distance `max_distance`.
- deduplicate: a convenience wrapper around `collapse_directional` and
  cluster-based collapsing.

The implementations are optimized for short UMI strings (length <= 16).
"""
from __future__ import annotations

from typing import Iterable, Dict, List, Tuple
from collections import Counter, defaultdict
import logging

from .clustering import hamming_distance, cluster as cluster_umis

logger = logging.getLogger(__name__)


def collapse_directional(umis: Iterable[str], max_distance: int = 1) -> Dict[str, int]:
    """Collapse UMIs using directional adjacency.

    Algorithm (simplified, robust variant):
    - Count all UMIs.
    - Sort UMIs by count descending.
    - For each UMI u in descending count order, merge any lower-count UMI v
      if hamming_distance(u, v) <= max_distance into u (add counts) and mark v
      as collapsed.

    This preserves high-confidence UMIs and collapses low-count errors.

    Args:
        umis: Iterable of UMI sequences (strings).
        max_distance: Maximum Hamming distance to consider a neighbor (default 1).

    Returns:
        Dict mapping representative UMI -> collapsed count.
    """
    counts = Counter(umis)
    if not counts:
        return {}

    umi_list = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    collapsed = {}
    seen = set()

    for umi, cnt in umi_list:
        if umi in seen:
            continue
        # Representative
        rep = umi
        rep_count = counts[umi]
        seen.add(umi)
        # find neighbours with lower counts
        for other, ocnt in umi_list:
            if other in seen:
                continue
            if ocnt > counts[umi]:
                # only collapse into higher-count nodes
                continue
            if hamming_distance(rep, other) <= max_distance:
                rep_count += ocnt
                seen.add(other)
        collapsed[rep] = rep_count

    return collapsed


def deduplicate(umis: Iterable[str], method: str = "directional", max_distance: int = 1) -> Dict[str, int]:
    """High-level deduplication API.

    Args:
        umis: Iterable of UMI strings.
        method: One of 'directional' or 'cluster'.
        max_distance: Hamming threshold for adjacency.

    Returns:
        Representative UMI -> deduplicated count
    """
    if method == "directional":
        return collapse_directional(umis, max_distance)
    elif method == "cluster":
        clusters = cluster_umis(list(umis), max_distance)
        # choose cluster representative as the most common UMI in cluster
        result = {}
        for rep, members in clusters.items():
            counter = Counter(members)
            top = counter.most_common(1)[0][0]
            result[top] = sum(counter.values())
        return result
    else:
        raise ValueError("Unsupported method: %s" % method)

