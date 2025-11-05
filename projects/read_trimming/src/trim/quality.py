"""Quality trimming helpers."""

from typing import Iterable


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
