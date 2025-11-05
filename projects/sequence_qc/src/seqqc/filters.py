"""Filtering helpers for sequence_qc.

Provides robust, dependency-free sequence filters suitable for transcript QC
workflows: length-based filtering and low-complexity filtering using both
Shannon entropy and a simple DUST-like score.
"""
from typing import List, Tuple
from collections import Counter
import math


def filter_by_length(seqs: List[str], min_len: int = 0, max_len: int | None = None) -> List[str]:
    if min_len < 0 or (max_len is not None and max_len < 0):
        raise ValueError("min_len and max_len must be non-negative")
    if max_len is None:
        return [s for s in seqs if len(s) >= min_len]
    return [s for s in seqs if min_len <= len(s) <= max_len]


def _shannon_entropy(s: str, k: int = 2) -> float:
    """Compute normalized Shannon entropy over k-mers (0..1).

    Normalization uses the maximum possible entropy for the observed number
    of distinct k-mers (i.e., log2(n_kmers)). Returns 0.0 for short strings.
    """
    if len(s) < k:
        return 0.0
    kmers = [s[i:i+k] for i in range(len(s) - k + 1)]
    counts = Counter(kmers)
    total = len(kmers)
    probs = [c / total for c in counts.values()]
    ent = -sum(p * math.log2(p) for p in probs if p > 0)
    max_ent = math.log2(len(counts)) if len(counts) > 1 else 0.0
    return 0.0 if max_ent == 0.0 else ent / max_ent


def _dust_score(s: str, k: int = 3) -> float:
    """Compute a simple DUST-like low-complexity score (lower is more complex).

    This implementation counts multiplicities of overlapping k-mers and
    computes a normalized collision score.
    """
    if len(s) < k:
        return 0.0
    kmers = [s[i:i+k] for i in range(len(s) - k + 1)]
    counts = Counter(kmers)
    total = len(kmers)
    # collision = sum(n*(n-1)/2) over counts; normalize to [0,1]
    collisions = sum(v * (v - 1) / 2.0 for v in counts.values())
    # maximum collisions occurs when all kmers identical: n*(n-1)/2
    max_coll = total * (total - 1) / 2.0 if total > 1 else 1.0
    return collisions / max_coll if max_coll > 0 else 0.0


def remove_low_complexity(seqs: List[str], entropy_threshold: float = 0.4, dust_threshold: float = 0.25) -> List[str]:
    """Filter out low-complexity sequences.

    A sequence is kept if its normalized k-mer Shannon entropy >= entropy_threshold
    AND its DUST-like collision score <= dust_threshold. Thresholds chosen
    reasonably for short reads; callers may tune them.
    """
    out: List[str] = []
    for s in seqs:
        e = _shannon_entropy(s, k=2)
        d = _dust_score(s, k=3)
        if e >= entropy_threshold and d <= dust_threshold:
            out.append(s)
    return out

