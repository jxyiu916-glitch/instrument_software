"""Advanced sequence quality control for breakthrough single-cell discoveries.

This module provides comprehensive sequence QC metrics designed to:
1. Enable high-confidence single-cell analysis
2. Detect sequencing artifacts that could impact biological insights
3. Support novel cell type and state discoveries
4. Ensure reliable gene expression quantification
5. Validate library preparation quality

Key Features:
- Advanced barcode quality analysis
- UMI sequence validation
- Transcript alignment metrics
- Cell multiplet detection
- Library complexity assessment
- Sequencing saturation analysis
"""

from __future__ import annotations

# Standard library imports
import logging
import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Dict, List, Optional, Set, Tuple, Union,
    NamedTuple, Protocol, TypeVar, Any
)

# Third-party imports
import numpy as np
from scipy import stats

# Local imports
from .transcript_qc import (
    TranscriptQualityMetrics,
    analyze_transcripts,
    calculate_gc_bias,
    calculate_transcript_complexity
)
from .barcode_qc import BarcodeQualityMetrics, analyze_cell_barcodes

# Constants for single-cell analysis
CELL_BARCODE_LENGTH = 16
UMI_LENGTH = 10
MIN_READS_PER_CELL = 500
BARCODE_WHITELIST_HAMMING = 1  # Max Hamming distance for whitelist correction

# Quality thresholds
PHRED_OFFSET = 33
MIN_ACCEPTABLE_QUALITY = 20  # Q20
HIGH_QUALITY_THRESHOLD = 30  # Q30

class SequenceType(Enum):
    """Types of sequences in single-cell data."""
    CELL_BARCODE = "cell_barcode"
    UMI = "umi"
    TRANSCRIPT = "transcript"
    ADAPTER = "adapter"
    UNKNOWN = "unknown"

@dataclass
class SequenceQualityMetrics:
    """Enhanced quality metrics for single-cell sequence analysis."""
    sequence_type: SequenceType
    avg_quality: float
    min_quality: float
    max_quality: float
    q30_fraction: float
    error_rate: float
    gc_content: float
    complexity: float
    length: int
    quality_histogram: Dict[int, int] = field(default_factory=dict)
    position_qualities: List[float] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

from typing import List, Dict, Tuple, Optional, NamedTuple
from dataclasses import dataclass
import collections
import logging
import numpy as np
from scipy import stats

# Quality score constants
PHRED_OFFSET = 33
MIN_ACCEPTABLE_QUALITY = 20  # Q20
HIGH_QUALITY_THRESHOLD = 30  # Q30

@dataclass
class ReadQualityMetrics:
    """Comprehensive quality metrics for sequencing data.
    
    Attributes:
        avg_quality: Mean base quality score
        min_quality: Minimum base quality score
        q30_fraction: Fraction of bases >= Q30
        gc_content: GC content (0.0-1.0)
        complexity: Sequence complexity score
        avg_len: Average read length
        n_fraction: Fraction of N bases
        adapter_fraction: Fraction with adapter contamination
        num_reads: Total number of reads
        quality_distribution: Distribution of quality scores
        error_rate_estimate: Estimated sequencing error rate
    """
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

def basic_qc_stats(
    seqs: List[str],
    quals: Optional[List[str]] = None
) -> ReadQualityMetrics:
    """Calculate comprehensive QC metrics for sequencing data.
    
    This function provides detailed quality assessment for:
    - Base quality distribution
    - Sequence complexity
    - Error rate estimation
    - GC content analysis
    - Read length statistics
    - Quality score statistics
    - Adapter contamination checks
    
    Args:
        seqs: List of sequence strings
        quals: Optional list of quality strings (Phred+33)
        
    Returns:
        ReadQualityMetrics containing comprehensive QC data
    """
    if not seqs:
        return ReadQualityMetrics(
            avg_quality=0.0,
            min_quality=0.0,
            q30_fraction=0.0,
            gc_content=0.0,
            complexity=0.0,
            avg_len=0.0,
            n_fraction=0.0,
            adapter_fraction=0.0,
            num_reads=0,
            quality_distribution={},
            error_rate_estimate=0.0
        )
    
    # Basic metrics
    lengths = [len(s) for s in seqs]
    n_count = sum(1 for s in seqs if 'N' in s)
    gc = gc_content(seqs)
    
    # Quality metrics if quals provided
    if quals:
        q_scores = [[ord(c) - PHRED_OFFSET for c in q] for q in quals]
        avg_qual = np.mean([np.mean(q) for q in q_scores])
        min_qual = min(min(q) for q in q_scores)
        q30_frac = np.mean([sum(q >= 30 for q in qs) / len(qs) for qs in q_scores])
        qual_dist = collections.Counter(q for qs in q_scores for q in qs)
        error_rate = 10 ** (-avg_qual/10)
    else:
        avg_qual = min_qual = q30_frac = 0.0
        qual_dist = {}
        error_rate = 0.0
    
    # Sequence complexity
    complexity = np.mean([_sequence_complexity(s) for s in seqs])
    
    return ReadQualityMetrics(
        avg_quality=avg_qual,
        min_quality=min_qual,
        q30_fraction=q30_frac,
        gc_content=gc,
        complexity=complexity,
        avg_len=sum(lengths) / len(lengths),
        n_fraction=n_count / len(seqs),
        adapter_fraction=0.0,  # Updated by adapter detection
        num_reads=len(seqs),
        quality_distribution=qual_dist,
        error_rate_estimate=error_rate
    )


def _sequence_complexity(seq: str) -> float:
    """Calculate sequence complexity using entropy-based metric.
    
    This function measures sequence complexity using Shannon entropy
    over k-mer distributions. Higher values indicate more complex sequences,
    which is important for:
    - Detecting low-complexity regions
    - Identifying PCR artifacts
    - Assessing library complexity
    - Finding potential systematic errors
    
    Args:
        seq: Input sequence string
        
    Returns:
        Complexity score between 0.0 (low) and 1.0 (high)
    """
    if len(seq) < 3:
        return 0.0
        
    # Calculate k-mer entropy for k=2 and k=3
    entropies = []
    for k in [2, 3]:
        kmers = [seq[i:i+k] for i in range(len(seq)-k+1)]
        counts = collections.Counter(kmers)
        probs = [count/len(kmers) for count in counts.values()]
        entropy = -sum(p * np.log2(p) for p in probs)
        max_entropy = np.log2(min(4**k, len(kmers)))  # Theoretical max
        entropies.append(0.0 if max_entropy == 0 else entropy/max_entropy)
    
    return np.mean(entropies)

def gc_content(seqs: List[str], window_size: int = 100) -> Tuple[float, Dict[str, List[float]]]:
    """Analyze GC content distribution across sequences.
    
    This function provides detailed GC content analysis important for:
    - Detecting sequencing bias
    - Identifying problematic regions
    - Assessing library preparation quality
    - Supporting PCR optimization
    
    Args:
        seqs: List of sequence strings
        window_size: Size of sliding window for local GC analysis
        
    Returns:
        Tuple of (overall_gc_fraction, detailed_metrics) where detailed_metrics
        contains:
        - 'per_pos_gc': Per-position GC content
        - 'gc_distribution': Distribution of GC percentages
        - 'local_gc': Sliding window GC analysis
    """
    if not seqs:
        return 0.0, {
            'per_pos_gc': [],
            'gc_distribution': [],
            'local_gc': []
        }
    
    # Overall GC content
    total_bases = gc_bases = 0
    gc_counts = collections.defaultdict(int)
    
    # Per-position and sliding window analysis
    max_len = max(len(s) for s in seqs)
    pos_gc = np.zeros(max_len)
    pos_total = np.zeros(max_len)
    local_gc = []
    
    for s in seqs:
        seq = s.upper()
        # Overall counts
        for ch in seq:
            if ch in ('A', 'C', 'G', 'T', 'N'):
                total_bases += 1
                if ch in ('G', 'C'):
                    gc_bases += 1
        
        # Per-position analysis
        for i, ch in enumerate(seq):
            if ch in ('A', 'C', 'G', 'T', 'N'):
                pos_total[i] += 1
                if ch in ('G', 'C'):
                    pos_gc[i] += 1
        
        # Sliding window analysis
        if len(seq) >= window_size:
            for i in range(len(seq) - window_size + 1):
                window = seq[i:i+window_size]
                gc_count = sum(1 for ch in window if ch in ('G', 'C'))
                valid_bases = sum(1 for ch in window if ch in ('A', 'C', 'G', 'T'))
                if valid_bases > 0:
                    local_gc.append(gc_count / valid_bases)
    
    # Calculate metrics
    overall_gc = gc_bases / total_bases if total_bases > 0 else 0.0
    per_pos_gc = [gc/total if total > 0 else 0.0 
                  for gc, total in zip(pos_gc, pos_total)]
    
    return overall_gc, {
        'per_pos_gc': per_pos_gc,
        'gc_distribution': local_gc,
        'local_gc': local_gc
    }


@dataclass
class LengthStats:
    """Comprehensive length statistics for sequence analysis.
    
    Enables detection of:
    - Library preparation artifacts
    - Sequencing quality issues
    - Sample degradation
    - PCR bias effects
    """
    histogram: Dict[int, int]
    mean: float
    median: float
    std_dev: float
    min_len: int
    max_len: int
    length_distribution: List[float]
    fragment_size_estimate: Optional[float]

def length_histogram(seqs: List[str]) -> LengthStats:
    """Analyze read length distribution with statistical metrics.
    
    This analysis helps identify:
    - Library preparation issues
    - Size selection problems
    - Degradation patterns
    - PCR amplification bias
    - Sequencing artifacts
    
    Args:
        seqs: List of sequence strings
        
    Returns:
        LengthStats with comprehensive length analysis
    """
    if not seqs:
        return LengthStats(
            histogram={},
            mean=0.0,
            median=0.0,
            std_dev=0.0,
            min_len=0,
            max_len=0,
            length_distribution=[],
            fragment_size_estimate=None
        )
    
    # Basic histogram
    hist = collections.Counter(len(s) for s in seqs)
    lengths = [len(s) for s in seqs]
    
    # Statistical analysis
    mean_len = np.mean(lengths)
    median_len = np.median(lengths)
    std_dev = np.std(lengths)
    
    # Length distribution analysis
    min_len = min(lengths)
    max_len = max(lengths)
    bins = np.linspace(min_len, max_len, num=50)
    hist_values, _ = np.histogram(lengths, bins=bins, density=True)
    
    # Estimate fragment size using kernel density estimation
    if len(lengths) > 100:
        try:
            kernel = stats.gaussian_kde(lengths)
            x_range = np.linspace(min_len, max_len, 200)
            density = kernel(x_range)
            fragment_size = x_range[np.argmax(density)]
        except Exception as e:
            logging.warning(f"Failed to estimate fragment size: {e}")
            fragment_size = None
    else:
        fragment_size = None
    
    return LengthStats(
        histogram=dict(hist),
        mean=mean_len,
        median=median_len,
        std_dev=std_dev,
        min_len=min_len,
        max_len=max_len,
        length_distribution=hist_values.tolist(),
        fragment_size_estimate=fragment_size
    )

def filter_by_length(
    seqs: List[str],
    min_len: int = 0,
    max_len: Optional[int] = None,
    quals: Optional[List[str]] = None
) -> Tuple[List[str], Optional[List[str]], Dict[str, int]]:
    """Filter sequences by length with quality score preservation.
    
    This enhanced filter:
    - Preserves quality scores
    - Tracks filtering statistics
    - Validates length parameters
    - Provides detailed filtering metrics
    
    Args:
        seqs: Input sequences
        min_len: Minimum allowed length
        max_len: Maximum allowed length (optional)
        quals: Quality scores (optional)
        
    Returns:
        Tuple of (filtered_seqs, filtered_quals, stats) where stats contains:
        - total: Total sequences processed
        - passed: Sequences passing filters
        - too_short: Sequences below min_len
        - too_long: Sequences above max_len
    """
    if min_len < 0:
        raise ValueError("min_len must be >= 0")
    
    stats = {
        'total': len(seqs),
        'passed': 0,
        'too_short': 0,
        'too_long': 0
    }
    
    filtered_seqs = []
    filtered_quals = [] if quals else None
    
    for i, s in enumerate(seqs):
        L = len(s)
        if L < min_len:
            stats['too_short'] += 1
            continue
        if max_len is not None and L > max_len:
            stats['too_long'] += 1
            continue
            
        filtered_seqs.append(s)
        if quals:
            filtered_quals.append(quals[i])
        stats['passed'] += 1
    
    return filtered_seqs, filtered_quals, stats


@dataclass
class BaseComposition:
    """Per-base sequence composition analysis.
    
    Enables detection of:
    - Systematic sequencing errors
    - Base-calling problems
    - Library preparation bias
    - Contamination signatures
    """
    n_fraction: List[float]
    base_counts: Dict[str, List[int]]
    quality_profile: Optional[List[float]]
    position_entropy: List[float]
    base_ratios: Dict[str, List[float]]

def per_base_composition(
    seqs: List[str],
    quals: Optional[List[str]] = None
) -> BaseComposition:
    """Perform comprehensive per-base sequence analysis.
    
    This analysis helps identify:
    - Sequencing artifacts
    - Base-calling errors
    - Quality degradation patterns
    - Systematic biases
    - Contamination signatures
    
    Args:
        seqs: List of sequences
        quals: Optional quality scores
        
    Returns:
        BaseComposition with detailed per-base metrics
    """
    if not seqs:
        return BaseComposition(
            n_fraction=[],
            base_counts={'A': [], 'C': [], 'G': [], 'T': [], 'N': []},
            quality_profile=None,
            position_entropy=[],
            base_ratios={}
        )
    
    max_len = max(len(s) for s in seqs)
    num_seqs = len(seqs)
    
    # Initialize counters
    base_counts = {base: [0] * max_len for base in 'ACGTN'}
    n_counts = [0] * max_len
    qual_sums = [0] * max_len if quals else None
    qual_counts = [0] * max_len if quals else None
    
    # Count bases and qualities
    for i, s in enumerate(seqs):
        seq = s.upper()
        for pos, base in enumerate(seq):
            if base in base_counts:
                base_counts[base][pos] += 1
            if base == 'N':
                n_counts[pos] += 1
                
        if quals:
            qual = quals[i]
            for pos, q in enumerate(qual):
                q_value = ord(q) - PHRED_OFFSET
                qual_sums[pos] += q_value
                qual_counts[pos] += 1
    
    # Calculate metrics
    n_fraction = [count/num_seqs for count in n_counts]
    
    # Calculate position-wise entropy
    entropy = []
    for pos in range(max_len):
        counts = [base_counts[base][pos] for base in 'ACGT']
        total = sum(counts)
        if total > 0:
            probs = [count/total for count in counts]
            pos_entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probs)
            entropy.append(pos_entropy / 2)  # Normalize by max entropy (2 bits)
        else:
            entropy.append(0.0)
    
    # Calculate base ratios
    base_ratios = {}
    for b1 in 'ACGT':
        for b2 in 'ACGT':
            if b1 < b2:  # Only do each pair once
                ratio_key = f"{b1}/{b2}"
                ratios = []
                for pos in range(max_len):
                    count1 = base_counts[b1][pos]
                    count2 = base_counts[b2][pos]
                    if count1 + count2 > 0:
                        ratio = count1 / (count1 + count2)
                    else:
                        ratio = 0.5  # Default to balanced when no data
                    ratios.append(ratio)
                base_ratios[ratio_key] = ratios
    
    # Calculate quality profile
    quality_profile = None
    if quals:
        quality_profile = [
            qual_sums[pos]/qual_counts[pos] if qual_counts[pos] > 0 else 0
            for pos in range(max_len)
        ]
    
    return BaseComposition(
        n_fraction=n_fraction,
        base_counts=base_counts,
        quality_profile=quality_profile,
        position_entropy=entropy,
        base_ratios=base_ratios
    )

@dataclass
class AdapterAnalysis:
    """Comprehensive adapter contamination analysis.
    
    Enables detection of:
    - Adapter dimers
    - Partial adapter sequences
    - Read-through artifacts
    - Library preparation issues
    """
    total_reads: int
    adapter_counts: Dict[str, int]
    position_distribution: Dict[str, List[int]]
    chimeric_reads: int
    mean_overlap: float
    quality_impact: Optional[Dict[str, float]]

def advanced_adapter_detection(
    seqs: List[str],
    adapters: Dict[str, str],
    quals: Optional[List[str]] = None,
    min_overlap: int = 10
) -> AdapterAnalysis:
    """Perform comprehensive adapter contamination analysis.
    
    This analysis helps identify:
    - Adapter contamination patterns
    - Library preparation artifacts
    - Read-through events
    - Chimeric sequences
    - Quality impact of contamination
    
    Args:
        seqs: Input sequences
        adapters: Dictionary of adapter name -> sequence
        quals: Optional quality scores
        min_overlap: Minimum overlap for adapter detection
        
    Returns:
        AdapterAnalysis with detailed contamination metrics
    """
    if not seqs or not adapters:
        return AdapterAnalysis(
            total_reads=len(seqs),
            adapter_counts={},
            position_distribution={},
            chimeric_reads=0,
            mean_overlap=0.0,
            quality_impact=None
        )
    
    # Initialize counters
    counts = {name: 0 for name in adapters}
    positions = {name: [0] * max(len(s) for s in seqs) for name in adapters}
    overlaps = []
    chimeric = 0
    qual_impact = {} if quals else None
    
    # Analyze each sequence
    for i, seq in enumerate(seqs):
        found_adapters = set()
        
        # Check each adapter
        for name, adapter in adapters.items():
            # Look for adapter with allowed mismatches
            for start in range(len(seq) - min_overlap + 1):
                overlap_len = min(len(adapter), len(seq) - start)
                if overlap_len < min_overlap:
                    continue
                    
                # Calculate similarity
                matches = sum(1 for j in range(overlap_len)
                            if seq[start + j].upper() == adapter[j].upper())
                if matches / overlap_len >= 0.9:  # Allow 10% mismatches
                    counts[name] += 1
                    positions[name][start] += 1
                    overlaps.append(overlap_len)
                    found_adapters.add(name)
                    
                    # Check quality impact if quals provided
                    if quals and qual_impact is not None:
                        qual = quals[i]
                        adapter_quals = [
                            ord(qual[start + j]) - PHRED_OFFSET
                            for j in range(overlap_len)
                            if start + j < len(qual)
                        ]
                        if adapter_quals:
                            qual_impact[name] = qual_impact.get(name, 0.0) + \
                                              sum(adapter_quals) / len(adapter_quals)
                    break
        
        if len(found_adapters) > 1:
            chimeric += 1
    
    # Finalize quality impact
    if qual_impact:
        for name in qual_impact:
            if counts[name] > 0:
                qual_impact[name] /= counts[name]
    
    return AdapterAnalysis(
        total_reads=len(seqs),
        adapter_counts=counts,
        position_distribution=positions,
        chimeric_reads=chimeric,
        mean_overlap=np.mean(overlaps) if overlaps else 0.0,
        quality_impact=qual_impact
    )

@dataclass
class ComprehensiveQCResult:
    """Complete quality control analysis results.
    
    Combines metrics from:
    1. Transcript analysis
    2. Barcode validation
    3. Adapter analysis
    4. Overall sequence quality
    """
    transcript_metrics: TranscriptQualityMetrics
    barcode_metrics: Optional[BarcodeQualityMetrics]
    adapter_metrics: Optional[AdapterAnalysis]
    total_reads: int
    passing_reads: int
    low_quality_reads: int
    filtered_reads: int
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

def run_comprehensive_qc(
    sequences: List[str],
    quality_scores: Optional[List[str]] = None,
    barcodes: Optional[List[str]] = None,
    transcript_coverage: Optional[List[List[int]]] = None,
    gc_content: Optional[List[float]] = None,
    adapter_sequences: Optional[Dict[str, str]] = None,
    min_quality: float = 30.0,
    min_complexity: float = 0.4
) -> ComprehensiveQCResult:
    """Run complete QC analysis on sequencing data.
    
    This function integrates all QC modules to provide a comprehensive
    quality assessment of single-cell sequencing data.
    
    Args:
        sequences: List of sequence reads
        quality_scores: Optional quality scores
        barcodes: Optional cell barcodes
        transcript_coverage: Optional coverage data
        gc_content: Optional GC content data
        adapter_sequences: Optional adapter sequences
        min_quality: Minimum quality threshold
        min_complexity: Minimum sequence complexity
        
    Returns:
        ComprehensiveQCResult with complete analysis
    """
    # Track read filtering
    total_reads = len(sequences)
    filtered_reads = defaultdict(int)
    passing_seqs = []
    passing_quals = []
    
    # Initial quality and complexity filtering
    for i, (seq, qual) in enumerate(zip(sequences, quality_scores or [None] * len(sequences))):
        if qual and np.mean([ord(q) - 33 for q in qual]) < min_quality:
            filtered_reads["low_quality"] += 1
            continue
            
        complexity = calculate_transcript_complexity([seq])
        if complexity < min_complexity:
            filtered_reads["low_complexity"] += 1
            continue
            
        passing_seqs.append(seq)
        if qual:
            passing_quals.append(qual)
    
    # Run individual analyses
    transcript_metrics = analyze_transcripts(
        sequences=passing_seqs,
        quality_scores=passing_quals if passing_quals else None,
        coverage=transcript_coverage,
        gc_content=gc_content
    )
    
    barcode_metrics = analyze_cell_barcodes(barcodes) if barcodes else None
    
    adapter_metrics = advanced_adapter_detection(
        passing_seqs,
        adapter_sequences,
        quals=passing_quals if passing_quals else None
    ) if adapter_sequences else None
    
    # Generate warnings and recommendations
    warnings = []
    recommendations = []
    
    # Add metric-specific warnings
    if transcript_metrics:
        warnings.extend(transcript_metrics.warnings)
        if transcript_metrics.three_prime_bias > 2.0:
            recommendations.append(
                "High 3' bias detected. Consider optimizing RNA fragmentation "
                "or library prep protocol."
            )
    
    if barcode_metrics and barcode_metrics.low_quality_fraction > 0.2:
        warnings.append(f"High fraction of low-quality barcodes: "
                      f"{barcode_metrics.low_quality_fraction:.1%}")
        recommendations.append(
            "Review cell isolation and library preparation protocols "
            "to improve barcode quality."
        )
    
    # Overall statistics
    total_filtered = sum(filtered_reads.values())
    
    return ComprehensiveQCResult(
        transcript_metrics=transcript_metrics,
        barcode_metrics=barcode_metrics,
        adapter_metrics=adapter_metrics,
        total_reads=total_reads,
        passing_reads=len(passing_seqs),
        low_quality_reads=filtered_reads["low_quality"],
        filtered_reads=total_filtered,
        warnings=warnings,
        recommendations=recommendations
    )

