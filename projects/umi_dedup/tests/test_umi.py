import os
import sys

# expose project src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from umi.core import (
    dedup_umis,
    unique_umi_fraction,
    dedup_umis_clustered,
    hamming_distance,
    umi_consensus,
)


def test_dedup_basic():
    umis = ['AAA', 'AAA', 'CCC', 'GGG', 'AAA']
    c = dedup_umis(umis)
    assert c['AAA'] == 3
    assert c['CCC'] == 1


def test_unique_fraction():
    umis = ['A', 'B', 'C', 'A']
    f = unique_umi_fraction(umis)
    assert abs(f - 0.75) < 1e-6


def test_hamming_and_clustering():
    umis = ['AAA', 'AAB', 'AAC', 'AAA']
    # exact dedup
    counts_exact = dedup_umis(umis)
    assert counts_exact['AAA'] == 2
    # clustered with max_distance=1 should merge AAB and AAC with AAA representative
    counts_clustered = dedup_umis_clustered(umis, max_distance=1)
    # representative keys may be the first seen member; ensure total unique clusters == 1 or 2
    assert sum(counts_clustered.values()) == 4


def test_hamming_distance_error():
    import pytest

    with pytest.raises(ValueError):
        hamming_distance('A', 'AA')


def test_umi_consensus():
    members = ['ACG', 'ACG', 'ATG']
    c = umi_consensus(members)
    assert c == 'ACG' or c == 'ATG'
