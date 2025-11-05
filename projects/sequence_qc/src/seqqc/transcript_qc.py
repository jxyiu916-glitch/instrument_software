"""Advanced transcript quality control for single-cell analysis.

This module provides specialized QC metrics for transcript sequences, enabling:
1. High-confidence gene expression analysis
2. Detection of RNA degradation
3. Assessment of library preparation quality
4. Validation of transcript coverage
5. Identification of sequencing artifacts
"""

from typing import Dict, List, Optional, Set, Tuple
import numpy as np
from scipy import stats
from collections import defaultdict
from dataclasses import dataclass, field

@dataclass
class TranscriptQualityMetrics:
    """Comprehensive quality metrics for transcript sequences.
    
    Enables:
    - RNA quality assessment
    - Coverage analysis
    - Degradation detection
    - Expression validation
    - Bias identification
    """
    total_transcripts: int
    mapped_fraction: float
    median_coverage: float
    three_prime_bias: float
    five_prime_bias: float
    gc_bias: float
    complexity: float
    error_rate: float
    quality_stats: Dict[str, float]
    coverage_distribution: List[float]
    warnings: List[str] = field(default_factory=list)

def analyze_transcripts(
    sequences: List[str],
    quality_scores: Optional[List[str]] = None,
    gc_content: Optional[List[float]] = None,
    coverage: Optional[List[List[int]]] = None,
    mapping_data: Optional[Dict[str, bool]] = None
) -> TranscriptQualityMetrics:
    """Perform comprehensive analysis of transcript sequences.
    
    This analysis enables:
    1. RNA quality assessment
    2. Library complexity evaluation
    3. Coverage uniformity analysis
    4. Bias detection
    5. Error rate estimation
    
    Args:
        sequences: List of transcript sequences
        quality_scores: Optional quality scores
        gc_content: Optional GC content per transcript
        coverage: Optional coverage depth data
        mapping_data: Optional mapping success data
        
    Returns:
        TranscriptQualityMetrics with comprehensive analysis
    """
    # Basic metrics
    total = len(sequences)
    mapped = sum(mapping_data.values()) if mapping_data else 0
    mapped_frac = mapped / total if total > 0 else 0.0
    
    # Coverage analysis
    if coverage:
        med_coverage = np.median([np.median(c) for c in coverage])
        coverage_dist = calculate_coverage_distribution(coverage)
        three_prime = calculate_three_prime_bias(coverage)
        five_prime = calculate_five_prime_bias(coverage)
    else:
        med_coverage = 0.0
        coverage_dist = []
        three_prime = 0.0
        five_prime = 0.0
    
    # GC bias analysis
    if gc_content and coverage:
        gc_bias = calculate_gc_bias(gc_content, coverage)
    else:
        gc_bias = 0.0
    
    # Quality analysis
    if quality_scores:
        quality_stats = analyze_quality_scores(quality_scores)
        error_rate = estimate_error_rate(quality_scores)
    else:
        quality_stats = {"mean": 0.0, "median": 0.0, "q30_fraction": 0.0}
        error_rate = 0.0
    
    # Calculate complexity
    complexity = calculate_transcript_complexity(sequences)
    
    # Generate warnings
    warnings = []
    if mapped_frac < 0.5:
        warnings.append(f"Low mapping rate: {mapped_frac:.1%}")
    if three_prime > 2.0:
        warnings.append("Strong 3' bias detected")
    if complexity < 0.4:
        warnings.append("Low sequence complexity")
    
    return TranscriptQualityMetrics(
        total_transcripts=total,
        mapped_fraction=mapped_frac,
        median_coverage=med_coverage,
        three_prime_bias=three_prime,
        five_prime_bias=five_prime,
        gc_bias=gc_bias,
        complexity=complexity,
        error_rate=error_rate,
        quality_stats=quality_stats,
        coverage_distribution=coverage_dist,
        warnings=warnings
    )

def calculate_coverage_distribution(
    coverage: List[List[int]],
    bins: int = 100
) -> List[float]:
    """Calculate normalized coverage distribution.
    
    Args:
        coverage: Coverage depth per position per transcript
        bins: Number of bins for distribution
        
    Returns:
        Normalized coverage distribution
    """
    if not coverage:
        return []
    
    # Normalize each transcript's coverage
    normalized = []
    for cov in coverage:
        if cov:
            mean_cov = np.mean(cov)
            if mean_cov > 0:
                normalized.extend([c / mean_cov for c in cov])
    
    if not normalized:
        return []
    
    # Calculate distribution
    hist, _ = np.histogram(normalized, bins=bins, density=True)
    return hist.tolist()

def calculate_three_prime_bias(coverage: List[List[int]]) -> float:
    """Calculate 3' coverage bias.
    
    Args:
        coverage: Coverage depth per position per transcript
        
    Returns:
        3' bias score (>1 indicates 3' bias)
    """
    if not coverage:
        return 0.0
    
    three_prime_scores = []
    for cov in coverage:
        if len(cov) >= 6:  # Need enough positions
            # Compare last 20% to middle region
            three_prime = np.mean(cov[-len(cov)//5:])
            middle = np.mean(cov[len(cov)//3:2*len(cov)//3])
            if middle > 0:
                three_prime_scores.append(three_prime / middle)
    
    return np.median(three_prime_scores) if three_prime_scores else 0.0

def calculate_five_prime_bias(coverage: List[List[int]]) -> float:
    """Calculate 5' coverage bias.
    
    Args:
        coverage: Coverage depth per position per transcript
        
    Returns:
        5' bias score (>1 indicates 5' bias)
    """
    if not coverage:
        return 0.0
    
    five_prime_scores = []
    for cov in coverage:
        if len(cov) >= 6:  # Need enough positions
            # Compare first 20% to middle region
            five_prime = np.mean(cov[:len(cov)//5])
            middle = np.mean(cov[len(cov)//3:2*len(cov)//3])
            if middle > 0:
                five_prime_scores.append(five_prime / middle)
    
    return np.median(five_prime_scores) if five_prime_scores else 0.0

def calculate_gc_bias(
    gc_content: List[float],
    coverage: List[List[int]]
) -> float:
    """Calculate GC bias in coverage.
    
    Args:
        gc_content: GC content per transcript
        coverage: Coverage depth per transcript
        
    Returns:
        GC bias score (0 indicates no bias)
    """
    if not gc_content or not coverage:
        return 0.0
    
    # Calculate mean coverage per transcript
    mean_coverage = [np.mean(cov) if cov else 0 for cov in coverage]
    
    # Calculate correlation between GC and coverage
    correlation, _ = stats.spearmanr(gc_content, mean_coverage)
    return abs(correlation) if not np.isnan(correlation) else 0.0

def calculate_transcript_complexity(sequences: List[str]) -> float:
    """Calculate transcript sequence complexity.
    
    Args:
        sequences: List of transcript sequences
        
    Returns:
        Complexity score between 0 and 1
    """
    if not sequences:
        return 0.0
    
    complexities = []
    for seq in sequences:
        if len(seq) >= 10:
            # Calculate entropy of 3-mers
            kmers = defaultdict(int)
            for i in range(len(seq) - 2):
                kmers[seq[i:i+3]] += 1
            
            total = sum(kmers.values())
            if total > 0:
                entropy = -sum((count/total) * np.log2(count/total) 
                             for count in kmers.values())
                max_entropy = np.log2(min(64, len(kmers)))  # 64 possible 3-mers
                if max_entropy > 0:
                    complexities.append(entropy / max_entropy)
    
    return np.mean(complexities) if complexities else 0.0

def analyze_quality_scores(quality_scores: List[str]) -> Dict[str, float]:
    """Analyze quality scores for transcripts.
    
    Args:
        quality_scores: Phred quality scores
        
    Returns:
        Dictionary of quality statistics
    """
    if not quality_scores:
        return {"mean": 0.0, "median": 0.0, "q30_fraction": 0.0}
    
    # Convert to numeric scores
    scores = [[ord(c) - 33 for c in qual] for qual in quality_scores]
    
    # Calculate statistics
    all_scores = [s for qual in scores for s in qual]
    mean_qual = np.mean(all_scores)
    median_qual = np.median(all_scores)
    q30 = sum(1 for s in all_scores if s >= 30) / len(all_scores)
    
    return {
        "mean": mean_qual,
        "median": median_qual,
        "q30_fraction": q30
    }

def estimate_error_rate(quality_scores: List[str]) -> float:
    """Estimate sequencing error rate from quality scores.
    
    Args:
        quality_scores: Phred quality scores
        
    Returns:
        Estimated error rate
    """
    if not quality_scores:
        return 0.0
    
    # Convert to error probabilities and average
    scores = [[ord(c) - 33 for c in qual] for qual in quality_scores]
    error_probs = [10 ** (-score/10) for qual in scores for score in qual]
    
    return np.mean(error_probs)