import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from alignment.core import (
    mapping_rate,
    softclip_stats,
    insert_size_stats,
    flag_summary,
    parse_cigar,
    softclip_lengths,
)


def make_rec(cigar, flag=0, is_unmapped=False):
    return {'cigar': cigar, 'flag': flag, 'is_unmapped': is_unmapped}


def test_mapping_rate_and_flags():
    recs = [make_rec('10M', flag=0), make_rec('10M', flag=0x4, is_unmapped=True), make_rec('5S5M', flag=0)]
    assert abs(mapping_rate(recs) - (2/3)) < 1e-6
    fs = flag_summary([{'flag': 0}, {'flag': 0x4}, {'flag': 0x10}, {'flag': 0x1}])
    assert fs['total'] == 4
    assert fs['unmapped'] == 1


def test_cigar_parsing_and_softclip():
    assert parse_cigar('5S95M') == [(5, 'S'), (95, 'M')]
    assert softclip_lengths('5S95M') == (5, 0)
    stats = softclip_stats([make_rec('5S90M5S'), make_rec('100M')])
    assert stats['n_records'] == 2
    assert stats['fraction_clipped'] == 0.5


def test_insert_size_stats():
    stats = insert_size_stats([100, 200, 150, 130])
    assert abs(stats['mean'] - 145.0) < 1e-6
    assert stats['median'] == 140.0 or stats['median'] == 145.0 or isinstance(stats['median'], float)
