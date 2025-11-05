"""Sequence statistics helpers."""
from dataclasses import dataclass
from typing import Dict, List
import collections


@dataclass
class LengthStats:
    min_len: int
    max_len: int
    mean_len: float
    median_len: float
    histogram: Dict[int, int]


def length_histogram(seqs: List[str]) -> LengthStats:
    if not seqs:
        return LengthStats(0,0,0.0,0.0,{})
    lengths = [len(s) for s in seqs]
    hist = collections.Counter(lengths)
    lengths_sorted = sorted(lengths)
    mean_len = sum(lengths)/len(lengths)
    median_len = lengths_sorted[len(lengths)//2]
    return LengthStats(min(lengths), max(lengths), mean_len, median_len, dict(hist))


@dataclass
class BaseComposition:
    per_pos: List[Dict[str, int]]
    overall: Dict[str, int]


def per_base_composition(seqs: List[str]) -> BaseComposition:
    if not seqs:
        return BaseComposition([], {})
    max_len = max(len(s) for s in seqs)
    per_pos = [collections.Counter() for _ in range(max_len)]
    overall = collections.Counter()
    for s in seqs:
        for i, ch in enumerate(s.upper()):
            per_pos[i][ch] += 1
            overall[ch] += 1
    return BaseComposition([dict(c) for c in per_pos], dict(overall))
