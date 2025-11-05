"""Variant filtering utilities.

Simple, dependency-free filters for variant lists produced by the demo
caller. These are intentionally conservative and easy to test.
"""
from typing import List, Dict, Any


def filter_variants(variants: List[Dict[str, Any]], min_af: float = 0.05, min_count: int = 1) -> List[Dict[str, Any]]:
    """Filter variant dictionary list by allele-fraction and alt count.

    Returns a filtered list preserving original ordering.
    """
    out: List[Dict[str, Any]] = []
    for v in variants:
        if v.get("alt_count", 0) >= min_count and v.get("af", 0.0) >= min_af:
            out.append(v)
    return out
