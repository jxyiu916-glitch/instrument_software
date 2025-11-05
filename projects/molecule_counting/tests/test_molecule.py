import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from molecule.core import count_molecules, collapse_umis_by_count


def test_count_molecules_basic():
    records = [('G1', 'U1'), ('G1', 'U1'), ('G1', 'U2'), ('G2', 'U1')]
    per_gene = count_molecules(records)
    assert per_gene['G1'] == 2  # U1 and U2
    assert per_gene['G2'] == 1


def test_collapse_min_reads():
    records = [('G1', 'U1'), ('G1', 'U1'), ('G1', 'U2')]
    collapsed = collapse_umis_by_count(records, min_reads=2)
    assert ('G1', 'U1') in collapsed and collapsed[('G1','U1')] == 2
    assert ('G1','U2') not in collapsed
