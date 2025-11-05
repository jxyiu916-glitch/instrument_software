"""Barcode correction helpers (Hamming distance, correction)."""

from typing import Set, Tuple


def hamming_distance(a: str, b: str) -> int:
    if len(a) != len(b):
        raise ValueError("Strings must be equal length for Hamming distance")
    return sum(ch1 != ch2 for ch1, ch2 in zip(a, b))


def correct_barcode(barcode: str, whitelist: Set[str], max_distance: int = 1) -> Tuple[str, int]:
    """Return (corrected_barcode, distance). If barcode already in whitelist returns (barcode,0).

    If no candidate within max_distance, returns (barcode, -1).
    Chooses the nearest whitelist entry (ties broken deterministically by sorted order).
    """
    if barcode in whitelist:
        return barcode, 0
    best = None
    best_d = max_distance + 1
    for w in whitelist:
        if len(w) != len(barcode):
            continue
        d = hamming_distance(barcode, w)
        if d <= max_distance and d < best_d:
            best = w
            best_d = d
        elif d <= max_distance and d == best_d:
            # tie-break
            if best is None or w < best:
                best = w
    if best is None:
        return barcode, -1
    return best, best_d
