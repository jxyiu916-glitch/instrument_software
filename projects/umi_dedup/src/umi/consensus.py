"""Consensus sequence computation for UMI clusters.

This module builds a consensus sequence from a list of reads/sequences
belonging to the same UMI cluster. The consensus algorithm supports simple
majority voting and an optional quality-aware consensus when per-base
qualities are provided.
"""
from __future__ import annotations

from typing import List, Optional, Sequence
from collections import Counter


def consensus(seqs: Sequence[str], quals: Optional[Sequence[str]] = None, tie_break: str = "N") -> str:
    """Compute consensus sequence for a cluster of sequences.

    Args:
        seqs: Sequence of nucleotide strings (may be variable length).
        quals: Optional sequence of per-read quality strings (Phred+33) matching `seqs`.
        tie_break: Base to use when there's a tie (default 'N').

    Returns:
        Consensus sequence string.
    """
    if not seqs:
        return ""
    L = max(len(s) for s in seqs)
    res = []
    for i in range(L):
        counts = Counter()
        if quals:
            # weight by quality
            for s, q in zip(seqs, quals):
                if i < len(s) and i < len(q):
                    base = s[i]
                    weight = ord(q[i]) - 33
                    counts[base] += max(1, weight)
        else:
            for s in seqs:
                if i < len(s):
                    counts[s[i]] += 1

        if counts:
            top = counts.most_common()
            if len(top) == 1 or top[0][1] > top[1][1]:
                res.append(top[0][0])
            else:
                # tie
                res.append(tie_break)
        else:
            res.append('N')
    return ''.join(res)

