"""Adapter detection and trimming helpers."""

from typing import Optional, Callable, List, Dict


def trim_adapter_exact(seq: str, adapter: str, max_mismatches: int = 0) -> str:
    """Trim adapter if found at end of read using exact or up-to-k mismatches naive search.

    Returns trimmed sequence (adapter removed) or original seq if not found.
    """
    if not adapter:
        return seq
    n = len(adapter)
    if len(seq) < n:
        return seq
    # check suffix windows of seq for adapter allowing up to max_mismatches
    for start in range(len(seq) - n, -1, -1):
        window = seq[start:start + n]
        mismatches = sum(a != b for a, b in zip(window, adapter))
        if mismatches <= max_mismatches:
            # trim adapter and any bases after it
            return seq[:start]
    return seq


def discover_adapters_kmer(reads: List[str], k: int = 10, top_n: int = 3) -> List[str]:
    """Simple adapter discovery via k-mer frequency at read tails.

    This function counts k-mers at the last `k+` positions of reads and
    reports the most frequent candidates (common adapter fragments). It's a
    lightweight heuristic intended for demo/diagnostic use; for production use
    a more sophisticated algorithm is recommended.
    """
    counts: Dict[str, int] = {}
    for r in reads:
        if len(r) < k:
            continue
        tail = r[-(k + 6):]  # include some context
        for i in range(max(0, len(tail) - k + 1)):
            kmer = tail[i:i + k]
            if len(kmer) == k:
                counts[kmer] = counts.get(kmer, 0) + 1
    # return top_n kmers sorted by count
    return [k for k, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_n]]


def detect_adapter_ml(seq: str, model_predict: Optional[Callable[[str], float]] = None, threshold: float = 0.5) -> bool:
    """Detect if adapter present using an ML model callable that returns probability [0,1].

    If model_predict is None, fall back to substring search for common adapters.
    """
    if model_predict is None:
        adapters = ["AGATCGGAAGAGC", "GATCGGAAGAGC", "CTGTCTCTTATA"]
        return any(ad in seq for ad in adapters)
    prob = float(model_predict(seq))
    return prob >= threshold


def try_cpp_trim_available() -> bool:
    """Return True if a compiled C++ trimming binary is discoverable.

    This implementation looks for a well-known executable in `./cpp/`.
    """
    import os

    exe = os.path.join(os.path.dirname(__file__), "..", "..", "cpp", "fast_trim")
    return os.path.exists(exe)
