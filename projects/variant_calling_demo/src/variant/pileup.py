"""Pileup utilities for the variant calling demo.

This module provides a small, dependency-free pileup generator that can be
used to compute base counts from aligned reads represented as
`Iterable[Tuple[int, str]]` (start_pos, seq). The implementation delegates to
`variant.core.pileup_from_reads` to keep behaviour consistent across the demo.
"""
from typing import Iterable, Tuple, Dict

from .core import pileup_from_reads


def generate_pileup(reads: Iterable[Tuple[int, str]]) -> Dict[int, Dict[str, int]]:
        """Return a mapping position -> base counts dict from aligned reads.

        Inputs:
            reads: iterable of (start_pos, sequence) tuples; sequences are treated as
                         raw bases and upper-cased.

        Output:
            dict mapping 0-based reference position -> dict(base -> count)
        """
        raw = pileup_from_reads(reads)
        # Convert defaultdicts to normal dicts for clean serialization
        return {pos: dict(counts) for pos, counts in raw.items()}
