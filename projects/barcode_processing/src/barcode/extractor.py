"""Barcode extraction helpers."""

from typing import Iterable


def extract_barcode_from_read(seq: str, bc_start: int, bc_len: int) -> str:
    """Extract a barcode substring from a read sequence.

    Efficiently extracts fixed-length cell barcodes from sequencing reads.
    Returns the substring or empty string if out of bounds.
    """
    if bc_start < 0 or bc_len <= 0:
        raise ValueError("bc_start must be >=0 and bc_len > 0")
    if bc_start + bc_len > len(seq):
        return ""
    return seq[bc_start: bc_start + bc_len]
