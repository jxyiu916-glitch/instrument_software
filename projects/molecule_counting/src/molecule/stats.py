"""Molecule counting statistics utilities.

Small, dependency-free helpers to summarize molecule count dictionaries.
"""
from typing import Dict, List, Tuple
import math


def umi_count_distribution(counts: Dict[str, int]) -> Dict[int, int]:
    """Return a mapping support_count -> number_of_umis having that support."""
    dist: Dict[int, int] = {}
    for v in counts.values():
        dist[v] = dist.get(v, 0) + 1
    return dist


def top_n(counts: Dict[str, int], n: int = 10) -> List[Tuple[str, int]]:
    """Return top-n (umi, count) pairs sorted by descending count."""
    return sorted(list(counts.items()), key=lambda kv: kv[1], reverse=True)[:n]


def distribution_summary(counts: Dict[str, int]) -> Dict[str, float]:
    """Return mean, median, sd for UMI support counts."""
    vals = list(counts.values())
    if not vals:
        return {"mean": 0.0, "median": 0.0, "sd": 0.0}
    mean = sum(vals) / len(vals)
    sorted_vals = sorted(vals)
    median = sorted_vals[len(vals) // 2]
    var = sum((x - mean) ** 2 for x in vals) / len(vals)
    sd = math.sqrt(var)
    return {"mean": mean, "median": median, "sd": sd}

