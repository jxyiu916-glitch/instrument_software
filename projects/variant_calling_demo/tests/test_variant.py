import os
import sys
import textwrap

# Ensure we can import the local src/ directory as a package during tests
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from variant.core import call_variants, pretty_print


def test_no_variant():
    ref = "ACGTACGTACGT"
    # reads match reference exactly
    reads = [(0, "ACGTAC"), (6, "GTACGT")]
    variants = call_variants(ref, reads, min_count=2, min_af=0.5)
    assert variants == []


def test_simple_snp_call():
    # create a reference and reads that introduce a SNP at position 4
    ref = "AAAAAAAAAA"  # all A
    # reads: three reads cover positions 2..6, two of them have A at pos 4, two have C
    reads = [
        (0, "AAAAA"),
        (0, "AACAA"),
        (0, "ACCAA"),
    ]
    # Position 2-based (0-index): position 2 is third base; we want position 2 to have variant
    variants = call_variants(ref, reads, min_count=2, min_af=0.4)
    # we expect one variant at pos=2 with alt C (two counts out of 3 -> af=0.666)
    assert len(variants) == 1
    v = variants[0]
    assert v["pos"] == 2
    assert v["ref"] == "A"
    assert v["alt"] == "C"
    assert v["alt_count"] == 2
    assert v["depth"] == 3
    assert v["af"] > 0.6


def test_pretty_print():
    variants = [
        {"pos": 2, "ref": "A", "alt": "C", "depth": 10, "alt_count": 4, "af": 0.4}
    ]
    s = pretty_print(variants)
    assert "pos=2" in s and "ref=A" in s and "alt=C" in s
