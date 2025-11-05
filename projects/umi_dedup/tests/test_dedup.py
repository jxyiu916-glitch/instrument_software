from umi.dedup import deduplicate, collapse_directional


def test_collapse_directional():
    umis = ['AAAA', 'AAAA', 'AAAT', 'AAAT', 'AAGT', 'CCCC']
    res = collapse_directional(umis, max_distance=1)
    # collapsed should have representatives and summed counts
    assert 'AAAA' in res
    assert res['AAAA'] >= 2


def test_deduplicate_cluster():
    umis = ['AAAA', 'AAAT', 'AAGT', 'CCCC']
    res = deduplicate(umis, method='cluster', max_distance=1)
    # result should map representative to counts
    assert isinstance(res, dict)
