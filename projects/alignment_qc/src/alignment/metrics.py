"""Alignment QC metrics.

Functions here compute common alignment QC metrics used in pipelines:
- mapping_rate
- insert_size_stats (mean, median, std)
- alignment_summary (aggregates basic fields)

These implementations are designed to be small, dependency-light, and
well-tested; for large BAM files prefer using pysam integration (optional).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Iterable, Tuple
import statistics


@dataclass
class InsertSizeStats:
    mean: float
    median: float
    std: float
    count: int


def mapping_rate(mapped: int, total: int) -> float:
    """Return simple mapping rate (mapped/total)."""
    if total <= 0:
        return 0.0
    return mapped / total


def insert_size_stats(sizes: Iterable[int]) -> InsertSizeStats:
    """Compute basic insert size statistics.

    Returns mean, median, standard deviation and count.
    """
    sizes_list = list(sizes)
    if not sizes_list:
        return InsertSizeStats(0.0, 0.0, 0.0, 0)
    mean = statistics.mean(sizes_list)
    median = statistics.median(sizes_list)
    std = statistics.pstdev(sizes_list) if len(sizes_list) > 1 else 0.0
    return InsertSizeStats(mean=mean, median=median, std=std, count=len(sizes_list))


def alignment_summary(mapped: int, unmapped: int, duplicates: int, total_reads: int) -> Dict[str, float]:
    """Return a small dictionary with common alignment summary metrics."""
    rate = mapping_rate(mapped, total_reads)
    dup_rate = duplicates / total_reads if total_reads > 0 else 0.0
    return {
        "mapping_rate": rate,
        "duplicate_rate": dup_rate,
        "mapped": mapped,
        "unmapped": unmapped,
        "total": total_reads,
    }

