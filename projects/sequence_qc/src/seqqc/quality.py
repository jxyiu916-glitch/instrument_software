"""Quality analysis helpers for sequence_qc.

Contains ReadQualityMetrics and functions for basic QC and GC analysis.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import collections
import numpy as np
from scipy import stats
import logging

# Quality score constants
PHRED_OFFSET = 33

@dataclass
class ReadQualityMetrics:
    avg_quality: float
    min_quality: float
    q30_fraction: float
    gc_content: float
    complexity: float
    avg_len: float
    n_fraction: float
    adapter_fraction: float
    num_reads: int
    quality_distribution: Dict[int, int]
    error_rate_estimate: float


def _sequence_complexity(seq: str) -> float:
    if len(seq) < 3:
        return 0.0
    entropies = []
    for k in [2, 3]:
        kmers = [seq[i:i+k] for i in range(len(seq)-k+1)]
        counts = collections.Counter(kmers)
        probs = [count/len(kmers) for count in counts.values()]
        entropy = -sum(p * np.log2(p) for p in probs)
        max_entropy = np.log2(min(4**k, len(kmers)))
        entropies.append(0.0 if max_entropy == 0 else entropy/max_entropy)
    return float(np.mean(entropies))


def gc_content(seqs: List[str], window_size: int = 100) -> Tuple[float, Dict[str, List[float]]]:
    if not seqs:
        return 0.0, {'per_pos_gc': [], 'gc_distribution': [], 'local_gc': []}
    total_bases = gc_bases = 0
    gc_counts = collections.defaultdict(int)
    max_len = max(len(s) for s in seqs)
    pos_gc = [0] * max_len
    pos_total = [0] * max_len
    for s in seqs:
        for i, ch in enumerate(s.upper()):
            if ch in 'GC':
                gc_bases += 1
            if ch in 'ATGCN':
                total_bases += 1
            if ch in 'GC':
                pos_gc[i] += 1
            pos_total[i] += 1
    overall = (gc_bases / total_bases) if total_bases > 0 else 0.0
    per_pos_gc = [pos_gc[i]/pos_total[i] if pos_total[i] > 0 else 0.0 for i in range(max_len)]
    # simple distribution
    gc_percentages = [ (s.count('G')+s.count('C'))/len(s) if len(s)>0 else 0.0 for s in seqs ]
    return overall, {'per_pos_gc': per_pos_gc, 'gc_distribution': gc_percentages, 'local_gc': []}


def basic_qc_stats(seqs: List[str], quals: Optional[List[str]] = None) -> ReadQualityMetrics:
    if not seqs:
        return ReadQualityMetrics(0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0,{ },0.0)
    lengths = [len(s) for s in seqs]
    n_count = sum(1 for s in seqs if 'N' in s)
    gc, _ = gc_content(seqs)
    if quals:
        q_scores = [[ord(c) - PHRED_OFFSET for c in q] for q in quals]
        avg_qual = float(np.mean([np.mean(q) for q in q_scores]))
        min_qual = int(min(min(q) for q in q_scores))
        q30_frac = float(np.mean([sum(q >= 30 for q in qs) / len(qs) for qs in q_scores]))
        qual_dist = collections.Counter(q for qs in q_scores for q in qs)
        error_rate = 10 ** (-avg_qual/10)
    else:
        avg_qual = min_qual = q30_frac = 0.0
        qual_dist = {}
        error_rate = 0.0
    complexity = float(np.mean([_sequence_complexity(s) for s in seqs]))
    return ReadQualityMetrics(
        avg_quality=avg_qual,
        min_quality=min_qual,
        q30_fraction=q30_frac,
        gc_content=gc,
        complexity=complexity,
        avg_len=sum(lengths)/len(lengths),
        n_fraction=n_count/len(seqs),
        adapter_fraction=0.0,
        num_reads=len(seqs),
        quality_distribution=dict(qual_dist),
        error_rate_estimate=error_rate
    )
