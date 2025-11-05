import os
import sys

# expose project src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from seqqc.core import (
    basic_qc_stats,
    gc_content,
    length_histogram,
    filter_by_length,
    per_base_n_fraction,
    simple_adapter_detection,
)


def test_basic_qc():
    seqs = ['ACTG', 'AANNT', 'ACT']
    s = basic_qc_stats(seqs)
    assert abs(s['avg_len'] - (4 + 5 + 3) / 3) < 1e-6
    assert abs(s['frac_N'] - (1/3)) < 1e-6


def test_gc_and_histogram_and_filter():
    seqs = ['GCGC', 'ATAT', 'NNNN', 'GCG']
    gc = gc_content(seqs)
    assert 0.0 <= gc <= 1.0
    hist = length_histogram(seqs)
    # three reads of length 4: 'GCGC', 'ATAT', 'NNNN'
    assert hist[4] == 3
    filtered = filter_by_length(seqs, min_len=4)
    assert len(filtered) == 3


def test_per_base_and_adapter():
    seqs = ['ACN', 'NCG', 'ACG']
    pb = per_base_n_fraction(seqs)
    # position 0: one N (index 1), position 1: one N (index 0), position2: one N (index 0)
    assert len(pb) == 3
    # simple adapter detection
    seqs2 = ['AAAADAPTER', 'TTT', 'ADAPTERXXX']
    assert simple_adapter_detection(seqs2, 'ADAPTER') == 2


def test_filter_invalid():
    import pytest

    with pytest.raises(ValueError):
        filter_by_length(['A'], min_len=-1)
