"""Integration tests for sequence QC functionality."""

import pytest
import numpy as np
from seqqc.core import run_comprehensive_qc

def test_comprehensive_qc():
    """Test complete QC pipeline with all features."""
    # Generate test data
    sequences = [
        "ACGTACGTACGTACGT",
        "GCTAGCTAGCTAGCTA",
        "TTATTAGCGATTATAA"
    ]
    quality_scores = [
        "IIIIIIIIIIIIIII",  # High quality
        "DDDDDDDDDDDDDDDD", # Medium quality
        "!!!!!!!!!!!!!!!"   # Low quality
    ]
    barcodes = [
        "AGCTACGTAGCTACGT",
        "TCGATCGAACGTACGT",
        "NNNNNNNNNNNNNNNN"  # Low quality barcode
    ]
    transcript_coverage = [
        [10, 10, 8, 6, 4],
        [12, 10, 8, 8, 6],
        [2, 2, 2, 2, 2]
    ]
    gc_content = [0.5, 0.6, 0.3]
    
    # Run comprehensive QC
    qc_results = run_comprehensive_qc(
        sequences=sequences,
        quality_scores=quality_scores,
        barcodes=barcodes,
        transcript_coverage=transcript_coverage,
        gc_content=gc_content,
        min_quality=20.0
    )
    
    # Verify results
    assert qc_results.total_reads == 3
    assert qc_results.filtered_reads > 0  # Some reads should be filtered
    assert qc_results.passing_reads < 3   # Not all reads should pass
    
    # Check transcript metrics
    assert qc_results.transcript_metrics.total_transcripts > 0
    assert qc_results.transcript_metrics.mapped_fraction >= 0
    assert qc_results.transcript_metrics.median_coverage > 0
    assert len(qc_results.transcript_metrics.coverage_distribution) > 0
    
    # Check barcode metrics
    assert qc_results.barcode_metrics.total_barcodes == 3
    assert qc_results.barcode_metrics.low_quality_barcodes > 0
    
    # Verify warnings and recommendations
    assert len(qc_results.warnings) > 0
    assert len(qc_results.recommendations) > 0

def test_minimal_qc():
    """Test QC with minimal inputs."""
    sequences = ["ACGTACGT", "GCTAGCTA"]
    
    qc_results = run_comprehensive_qc(
        sequences=sequences,
        min_quality=20.0
    )
    
    assert qc_results.total_reads == 2
    assert qc_results.transcript_metrics is not None
    assert qc_results.barcode_metrics is None  # No barcodes provided
    assert qc_results.adapter_metrics is None  # No adapters provided

def test_edge_cases():
    """Test QC with edge cases."""
    # Empty input
    qc_results = run_comprehensive_qc(sequences=[])
    assert qc_results.total_reads == 0
    assert len(qc_results.warnings) > 0
    
    # Single sequence
    qc_results = run_comprehensive_qc(sequences=["ACGT"])
    assert qc_results.total_reads == 1
    assert qc_results.transcript_metrics is not None
    
    # All low quality
    sequences = ["AAAA", "AAAA"]
    quality_scores = ["!!!!", "!!!!"]
    qc_results = run_comprehensive_qc(
        sequences=sequences,
        quality_scores=quality_scores,
        min_quality=30.0
    )
    assert qc_results.low_quality_reads > 0
    assert len(qc_results.warnings) > 0

def test_quality_thresholds():
    """Test different quality thresholds."""
    sequences = ["ACGTACGT"] * 3
    quality_scores = [
        "IIIIIIII",  # High quality
        "DDDDDDDD",  # Medium quality
        "!!!!!!!"    # Low quality
    ]
    
    # Strict quality threshold
    strict_qc = run_comprehensive_qc(
        sequences=sequences,
        quality_scores=quality_scores,
        min_quality=35.0
    )
    
    # Lenient quality threshold
    lenient_qc = run_comprehensive_qc(
        sequences=sequences,
        quality_scores=quality_scores,
        min_quality=15.0
    )
    
    assert strict_qc.passing_reads < lenient_qc.passing_reads