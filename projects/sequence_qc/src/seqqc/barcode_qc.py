"""Advanced cell barcode quality control for single-cell analysis.

This module provides specialized QC metrics for cell barcodes, enabling:
1. High-confidence cell calling
2. Multiplet detection and resolution
3. Barcode error correction
4. Library complexity assessment
5. Cell count validation
"""

from typing import Dict, List, Optional, Set, Tuple
import numpy as np
from scipy import stats
from collections import defaultdict
from dataclasses import dataclass, field

# Configuration constants
# Maximum Hamming distance allowed when correcting barcodes against a whitelist.
# Kept local to avoid circular imports with core module.
BARCODE_WHITELIST_HAMMING = 1

@dataclass
class BarcodeQualityMetrics:
    """Comprehensive quality metrics for cell barcodes.
    
    Enables:
    - Accurate cell count estimation
    - Multiplet detection
    - Library quality assessment
    - Error rate calculation
    - Sequencing saturation analysis
    """
    total_barcodes: int
    valid_barcodes: int
    estimated_cell_count: int
    mean_reads_per_cell: float
    sequencing_saturation: float
    estimated_multiplet_rate: float
    median_umis_per_cell: float
    complexity_score: float
    error_correction_stats: Dict[str, int]
    warnings: List[str] = field(default_factory=list)
    quality_distribution: Dict[int, int] = field(default_factory=dict)

def analyze_cell_barcodes(
    barcodes: List[str],
    reads_per_barcode: Dict[str, int],
    whitelist: Optional[Set[str]] = None,
    umi_counts: Optional[Dict[str, int]] = None,
    quality_scores: Optional[Dict[str, List[int]]] = None
) -> BarcodeQualityMetrics:
    """Perform comprehensive analysis of cell barcodes.
    
    This analysis enables:
    1. Accurate cell count estimation
    2. Detection of barcode sequencing errors
    3. Assessment of library complexity
    4. Identification of potential multiplets
    5. Quality control of cell calling
    
    Args:
        barcodes: List of observed cell barcodes
        reads_per_barcode: Number of reads per barcode
        whitelist: Optional set of valid cell barcodes
        umi_counts: Optional count of UMIs per barcode
        quality_scores: Optional quality scores per barcode
        
    Returns:
        BarcodeQualityMetrics with comprehensive analysis results
    """
    # Basic counts
    total_barcodes = len(barcodes)
    total_reads = sum(reads_per_barcode.values())
    
    # Cell calling and error correction
    if whitelist:
        valid_bcs, correction_stats = correct_cell_barcodes(barcodes, whitelist)
    else:
        valid_bcs = set(barcodes)
        correction_stats = {"exact": len(barcodes), "corrected": 0, "rejected": 0}
    
    # Estimate cell count using knee-point detection
    sorted_counts = sorted(reads_per_barcode.values(), reverse=True)
    cell_count = estimate_cell_count(sorted_counts)
    
    # Calculate sequencing saturation
    if umi_counts:
        saturation = calculate_sequencing_saturation(umi_counts)
        median_umis = np.median(list(umi_counts.values()))
    else:
        saturation = 0.0
        median_umis = 0.0
    
    # Estimate multiplet rate
    multiplet_rate = estimate_multiplet_rate(
        reads_per_barcode,
        cell_count,
        total_reads
    )
    
    # Calculate complexity score
    complexity = calculate_library_complexity(
        valid_bcs,
        reads_per_barcode,
        umi_counts
    )
    
    # Generate quality distribution if scores available
    qual_dist = {}
    if quality_scores:
        all_scores = [q for scores in quality_scores.values() for q in scores]
        qual_dist = {
            score: count for score, count in 
            zip(*np.unique(all_scores, return_counts=True))
        }
    
    # Generate warnings
    warnings = []
    if multiplet_rate > 0.1:
        warnings.append(
            f"High multiplet rate detected: {multiplet_rate:.1%}"
        )
    if saturation < 0.5:
        warnings.append(
            f"Low sequencing saturation: {saturation:.1%}"
        )
    if cell_count < 100:
        warnings.append(
            f"Low cell count detected: {cell_count}"
        )
    
    return BarcodeQualityMetrics(
        total_barcodes=total_barcodes,
        valid_barcodes=len(valid_bcs),
        estimated_cell_count=cell_count,
        mean_reads_per_cell=total_reads / cell_count if cell_count > 0 else 0,
        sequencing_saturation=saturation,
        estimated_multiplet_rate=multiplet_rate,
        median_umis_per_cell=median_umis,
        complexity_score=complexity,
        error_correction_stats=correction_stats,
        warnings=warnings,
        quality_distribution=qual_dist
    )

def correct_cell_barcodes(
    barcodes: List[str],
    whitelist: Set[str]
) -> Tuple[Set[str], Dict[str, int]]:
    """Correct cell barcodes using whitelist with error allowance.
    
    Args:
        barcodes: Observed barcodes
        whitelist: Set of valid barcodes
        
    Returns:
        Tuple of (corrected barcodes, correction statistics)
    """
    stats = {"exact": 0, "corrected": 0, "rejected": 0}
    corrected = set()
    
    for bc in barcodes:
        if bc in whitelist:
            corrected.add(bc)
            stats["exact"] += 1
            continue
            
        # Try to correct with Hamming distance 1
        found_match = False
        for valid_bc in whitelist:
            if hamming_distance(bc, valid_bc) <= BARCODE_WHITELIST_HAMMING:
                corrected.add(valid_bc)
                stats["corrected"] += 1
                found_match = True
                break
                
        if not found_match:
            stats["rejected"] += 1
    
    return corrected, stats

def estimate_cell_count(
    sorted_counts: List[int],
    threshold_factor: float = 0.1
) -> int:
    """Estimate number of cells using knee-point detection.
    
    Args:
        sorted_counts: Read counts per barcode (sorted descending)
        threshold_factor: Factor for knee point detection
        
    Returns:
        Estimated number of cells
    """
    if not sorted_counts:
        return 0
        
    # Calculate differences between consecutive points
    diffs = np.diff(sorted_counts)
    
    # Find the knee point where the difference becomes small
    threshold = np.max(diffs) * threshold_factor
    knee_idx = np.where(diffs > -threshold)[0]
    if len(knee_idx) > 0:
        return knee_idx[0] + 1
    return 1

def calculate_sequencing_saturation(
    umi_counts: Dict[str, int]
) -> float:
    """Calculate sequencing saturation from UMI counts.
    
    Args:
        umi_counts: Dictionary of UMI counts per cell
        
    Returns:
        Saturation value between 0 and 1
    """
    if not umi_counts:
        return 0.0
    
    # Use total UMIs vs unique UMIs
    total_umis = sum(umi_counts.values())
    unique_umis = len(set(umi_counts.keys()))
    
    if total_umis == 0:
        return 0.0
    return 1.0 - (unique_umis / total_umis)

def estimate_multiplet_rate(
    reads_per_barcode: Dict[str, int],
    estimated_cells: int,
    total_reads: int,
    poisson_threshold: float = 2.0
) -> float:
    """Estimate cell multiplet rate using read distribution.
    
    Args:
        reads_per_barcode: Reads per barcode
        estimated_cells: Estimated number of cells
        total_reads: Total number of reads
        poisson_threshold: Threshold for multiplet calling
        
    Returns:
        Estimated multiplet rate between 0 and 1
    """
    if estimated_cells == 0 or total_reads == 0:
        return 0.0
    
    # Expected reads per cell
    expected_reads = total_reads / estimated_cells
    
    # Count barcodes with significantly more reads than expected
    multiplets = sum(
        1 for count in reads_per_barcode.values()
        if count > expected_reads * poisson_threshold
    )
    
    return multiplets / estimated_cells if estimated_cells > 0 else 0.0

def calculate_library_complexity(
    valid_barcodes: Set[str],
    reads_per_barcode: Dict[str, int],
    umi_counts: Optional[Dict[str, int]] = None
) -> float:
    """Calculate library complexity score.
    
    Args:
        valid_barcodes: Set of valid cell barcodes
        reads_per_barcode: Reads per barcode
        umi_counts: Optional UMI counts per barcode
        
    Returns:
        Complexity score between 0 and 1
    """
    if not valid_barcodes:
        return 0.0
    
    # Use UMI information if available
    if umi_counts:
        umi_ratios = [
            len(set(umi_counts.get(bc, []))) / reads_per_barcode.get(bc, 1)
            for bc in valid_barcodes
        ]
        return np.mean(umi_ratios) if umi_ratios else 0.0
    
    # Fallback to read count distribution
    counts = [reads_per_barcode.get(bc, 0) for bc in valid_barcodes]
    if not counts:
        return 0.0
    
    # Use coefficient of variation as complexity measure
    mean_reads = np.mean(counts)
    if mean_reads == 0:
        return 0.0
    cv = np.std(counts) / mean_reads
    return 1.0 / (1.0 + cv)  # Transform to 0-1 scale

def hamming_distance(s1: str, s2: str) -> int:
    """Calculate Hamming distance between two strings."""
    if len(s1) != len(s2):
        return len(s1) + len(s2)  # Maximum possible distance
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))