"""High-level caller API for the variant calling demo.

This module provides a thin, well-documented interface around the core
calling implementation found in `variant.core`. The separation helps unit
testing and keeps the demo architecture modular.
"""
from typing import Iterable, Tuple, List, Dict, Any

from .core import call_variants as _core_call_variants


def call_variants(ref: str, reads: Iterable[Tuple[int, str]], min_count: int = 2, min_af: float = 0.2) -> List[Dict[str, Any]]:
    """Call variants from reference and aligned reads.

    Delegates to the core demo implementation. Kept as an explicit wrapper so
    future improvements (e.g., multithreading or vectorized callers) can be
    inserted without changing the public test surface.
    """
    return _core_call_variants(ref, reads, min_count=min_count, min_af=min_af)
