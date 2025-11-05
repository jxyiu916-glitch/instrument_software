"""Unit tests for transcript QC functionality."""

import pytest
import numpy as np
from seqqc.transcript_qc import (
    TranscriptQualityMetrics,
    analyze_transcripts,
    calculate_coverage_distribution,
    calculate_three_prime_bias,
    calculate_five_prime_bias,
    calculate_gc_bias,
    calculate_transcript_complexity,
    analyze_quality_scores,
    estimate_error_rate
)

def test_analyze_transcripts_basic():
    """Test basic transcript analysis with minimal data."""
    sequences = ["ACGTACGTAC", "GCTAGCTAGT", "TTATTAGCGA"]
    quality_scores = ["FFFFFFFFFF", "FFFFFFFFFF", "FFFFFFFFFF"]
    
    metrics = analyze_transcripts(
        sequences=sequences,
        quality_scores=quality_scores
    )
    
    assert isinstance(metrics, TranscriptQualityMetrics)
    assert metrics.total_transcripts == 3
    assert metrics.complexity > 0
    assert metrics.error_rate >= 0
    assert isinstance(metrics.warnings, list)

def test_analyze_transcripts_with_coverage():
    """Test transcript analysis with coverage data."""
    sequences = ["ACGTACGTAC", "GCTAGCTAGT"]
    coverage = [[10, 10, 8, 6, 4], [12, 10, 8, 8, 6]]
    gc_content = [0.5, 0.6]
    
    metrics = analyze_transcripts(
        sequences=sequences,
        coverage=coverage,
        gc_content=gc_content
    )
    
    assert metrics.median_coverage > 0
    assert metrics.three_prime_bias >= 0
    assert metrics.five_prime_bias >= 0
    assert metrics.gc_bias >= 0
    assert len(metrics.coverage_distribution) > 0

def test_coverage_distribution():
    """Test coverage distribution calculation."""
    coverage = [[10, 8, 6, 4], [12, 10, 8, 6]]
    dist = calculate_coverage_distribution(coverage, bins=10)
    
    assert len(dist) == 10
    assert all(x >= 0 for x in dist)
    assert abs(sum(dist) - 1.0) < 0.01  # Should be normalized

def test_three_prime_bias():
    """Test 3' bias calculation."""
    # Test case with strong 3' bias
    coverage = [[2, 4, 6, 8, 10], [4, 6, 8, 10, 12]]
    bias = calculate_three_prime_bias(coverage)
    assert bias > 1.0  # Should indicate 3' bias
    
    # Test case with no bias
    coverage = [[10, 10, 10, 10, 10], [8, 8, 8, 8, 8]]
    bias = calculate_three_prime_bias(coverage)
    assert abs(bias - 1.0) < 0.1  # Should be close to 1.0

def test_five_prime_bias():
    """Test 5' bias calculation."""
    # Test case with strong 5' bias
    coverage = [[10, 8, 6, 4, 2], [12, 10, 8, 6, 4]]
    bias = calculate_five_prime_bias(coverage)
    assert bias > 1.0  # Should indicate 5' bias
    
    # Test case with no bias
    coverage = [[10, 10, 10, 10, 10], [8, 8, 8, 8, 8]]
    bias = calculate_five_prime_bias(coverage)
    assert abs(bias - 1.0) < 0.1  # Should be close to 1.0

def test_gc_bias():
    """Test GC bias calculation."""
    gc_content = [0.3, 0.4, 0.5, 0.6]
    # Coverage correlating with GC content
    coverage = [[2, 2, 2], [4, 4, 4], [6, 6, 6], [8, 8, 8]]
    bias = calculate_gc_bias(gc_content, coverage)
    assert bias > 0.9  # Should show strong correlation
    
    # No correlation case
    coverage = [[5, 5, 5]] * 4
    bias = calculate_gc_bias(gc_content, coverage)
    assert bias < 0.1  # Should show no correlation

def test_transcript_complexity():
    """Test transcript complexity calculation."""
    # High complexity sequence
    high_complexity = ["ACGTACGTACGTACGT"]
    complexity = calculate_transcript_complexity(high_complexity)
    assert complexity > 0.8  # Should be high
    
    # Low complexity sequence
    low_complexity = ["AAAAAAAAAAAAAAAA"]
    complexity = calculate_transcript_complexity(low_complexity)
    assert complexity < 0.2  # Should be low

def test_quality_score_analysis():
    """Test quality score analysis."""
    # High quality scores
    high_qual = ["IIIIIIIII"]  # ASCII 73, Phred 40
    stats = analyze_quality_scores(high_qual)
    assert stats["mean"] > 35
    assert stats["q30_fraction"] > 0.99
    
    # Low quality scores
    low_qual = ["!!!!!!!!!"]  # ASCII 33, Phred 0
    stats = analyze_quality_scores(low_qual)
    assert stats["mean"] < 5
    assert stats["q30_fraction"] < 0.01

def test_error_rate_estimation():
    """Test error rate estimation."""
    # High quality (low error)
    high_qual = ["IIIIIIIII"]  # Phred 40
    error_rate = estimate_error_rate(high_qual)
    assert error_rate < 0.0001
    
    # Low quality (high error)
    low_qual = ["!!!!!!!!!"]  # Phred 0
    error_rate = estimate_error_rate(low_qual)
    assert error_rate > 0.1

def test_empty_inputs():
    """Test handling of empty inputs."""
    metrics = analyze_transcripts(sequences=[])
    assert metrics.total_transcripts == 0
    assert metrics.mapped_fraction == 0.0
    assert metrics.complexity == 0.0
    assert len(metrics.warnings) > 0

def test_invalid_inputs():
    """Test handling of invalid inputs."""
    # Mismatched lengths
    with pytest.raises(Exception):
        _ = calculate_gc_bias(
            gc_content=[0.5],
            coverage=[[1, 2], [3, 4]]  # More coverage entries than GC values
        )
    
    # Invalid quality scores
    with pytest.raises(Exception):
        _ = analyze_quality_scores(["invalid!"])  # Invalid ASCII range

def test_edge_cases():
    """Test edge cases in transcript analysis."""
    # Single base sequences
    sequences = ["A", "T", "G"]
    metrics = analyze_transcripts(sequences=sequences)
    assert metrics.complexity == 0.0  # Too short for valid complexity
    
    # All identical sequences
    sequences = ["ACGT"] * 10
    metrics = analyze_transcripts(sequences=sequences)
    assert metrics.complexity < 0.5  # Should indicate low diversity