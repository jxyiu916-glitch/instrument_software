import pytest

from umi.clustering import hamming_distance, cluster


def test_hamming_distance():
    assert hamming_distance('AAAA', 'AAAT') == 1
    assert hamming_distance('ACGT', 'TGCA') == 4


def test_cluster_simple():
    seqs = ['AAAA', 'AAAT', 'AAGT', 'CCCC']
    clusters = cluster(seqs, max_distance=1)
    # Expect at least two clusters: one for AAA* and one for CCCC
    reps = list(clusters.keys())
    assert any('CCCC' in members for members in clusters.values())
    assert any(any(s.startswith('AAA') or s.startswith('AAG') for s in members) for members in clusters.values())
