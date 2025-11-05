from typing import Iterable, Tuple, List, Callable, Optional


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


def quality_trim_tail(seq: str, quals: Iterable[int], min_quality: int = 20) -> str:
    """Trim low-quality bases from 3' end using a simple tail-trim rule.

    quals is an iterable of integer quality scores aligned with seq.
    """
    q = list(quals)
    if len(q) != len(seq):
        raise ValueError("quals length must match seq length")
    # find last position from left where quality >= min_quality and keep up to that
    last_good = -1
    for i, qi in enumerate(q):
        if qi >= min_quality:
            last_good = i
    if last_good == -1:
        return ''
    return seq[: last_good + 1]


def sliding_window_trim(seq: str, quals: Iterable[int], window: int = 4, min_avg: int = 20) -> str:
    """Trim from 3' end using sliding window average quality threshold.

    Returns trimmed sequence.
    """
    q = list(quals)
    if len(q) != len(seq):
        raise ValueError("quals length must match seq length")
    L = len(q)
    # walk windows from 5' to 3'
    cut = L
    for i in range(L - window + 1):
        win = q[i:i + window]
        avg = sum(win) / window
        # if average drops below threshold, mark cut (keep up to i+1)
        if avg < min_avg:
            cut = i + 1
            break
    return seq[:cut]


def detect_adapter_ml(seq: str, model_predict: Optional[Callable[[str], float]] = None, threshold: float = 0.5) -> bool:
    """Detect if adapter present using an ML model callable that returns probability [0,1].

    If model_predict is None, fall back to substring search for a canonical adapter (common sequences).
    """
    if model_predict is None:
        # naive fallback: check for common Illumina adapter fragments
        adapters = ['AGATCGGAAGAGC', 'GATCGGAAGAGC']
        return any(ad in seq for ad in adapters)
    prob = float(model_predict(seq))
    return prob >= threshold


def try_cpp_trim_available() -> bool:
    """Placeholder: indicate if a compiled C++ trimming binary is available.

    For now returns False; future work: compile `cpp/fast_trim.cpp` and expose via Python bindings.
    """
    return False
