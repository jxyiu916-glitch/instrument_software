import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from barcode.core import (
    extract_barcode_from_read,
    build_whitelist,
    correct_barcode,
    barcode_counts,
    top_barcodes,
)


def test_extract_barcode():
    seq = 'AAACCCGGGTTT'
    assert extract_barcode_from_read(seq, 3, 4) == 'CCCG'
    assert extract_barcode_from_read(seq, 9, 4) == ''


def test_correct_barcode_basic():
    wl = build_whitelist(['AAAA', 'AAAT', 'AATT'])
    b, d = correct_barcode('AAGA', wl, max_distance=1)
    # nearest is 'AAAA' at distance 1
    assert d == 1
    assert b in {'AAAA'}


def test_counts_and_top():
    b = ['BC1', 'BC1', 'BC2', 'BC3', 'BC1']
    counts = barcode_counts(b)
    assert counts['BC1'] == 3
    tb = top_barcodes(counts, n=2)
    assert tb[0][0] == 'BC1'
    assert tb[1][0] in {'BC2','BC3'}
