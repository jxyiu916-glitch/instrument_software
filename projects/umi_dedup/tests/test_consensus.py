from umi.consensus import consensus


def test_consensus_majority():
    seqs = ['ACGT', 'ACGT', 'ACGA']
    res = consensus(seqs)
    assert res == 'ACGT'


def test_consensus_quality():
    seqs = ['ACGT', 'ACGA']
    quals = ['IIII', '!!!!']  # high qual for first, low for second
    res = consensus(seqs, quals=quals)
    assert res == 'ACGT'
