"""Alignment statistics helpers.

Small functions used by alignment QC: coverage summaries, insert-size
statistics and duplicate rate estimation. These are intentionally
dependency-free and focused on clarity rather than extreme performance.
"""
from typing import List, Dict, Tuple
import math


def coverage_by_position(positions: List[int]) -> Dict[str, float]:
    if not positions:
        return {"mean": 0.0, "max": 0}
    return {"mean": sum(positions) / len(positions), "max": max(positions), "median": sorted(positions)[len(positions) // 2]}


def duplicate_rate(duplicate_counts: List[int]) -> float:
    """Estimate duplicate rate as fraction of unique reads with count==1 vs >1."""
    if not duplicate_counts:
        return 0.0
    n_total = len(duplicate_counts)
    n_dup = sum(1 for c in duplicate_counts if c > 1)
    return n_dup / n_total


def insert_size_stats(sizes: List[int]) -> Dict[str, float]:
    """Return simple statistics (mean, median, sd) for insert sizes."""
    if not sizes:
        return {"mean": 0.0, "median": 0.0, "sd": 0.0}
    mean = sum(sizes) / len(sizes)
    sorted_sizes = sorted(sizes)
    median = sorted_sizes[len(sizes) // 2]
    var = sum((x - mean) ** 2 for x in sizes) / len(sizes)
    sd = math.sqrt(var)
    return {"mean": mean, "median": median, "sd": sd}


def mapping_rate(mapped: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return mapped / total

