import os
import sys

TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from seqqc.filters import remove_low_complexity, filter_by_length


def test_filter_by_length_basic():
    seqs = ['A'*5, 'A'*10, 'A'*20]
    out = filter_by_length(seqs, min_len=6, max_len=15)
    assert out == ['A'*10]


def test_remove_low_complexity():
    seqs = ['AAAAAAAAAA', 'ACGTACGTAC', 'ATATATATAT', 'ACACACGTGT']
    # Only high-entropy sequence should remain
    out = remove_low_complexity(seqs, entropy_threshold=0.5, dust_threshold=0.5)
    assert 'ACGTACGTAC' in out
    assert 'AAAAAAAAAA' not in out
