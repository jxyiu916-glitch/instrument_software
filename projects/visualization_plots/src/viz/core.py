from typing import Sequence, Tuple, Callable, List, Optional
import math

# Lightweight plotting & diagnostics helpers. Functions try to avoid hard matplotlib dependencies for tests,
# but will return data that can be plotted by callers. A small plotting wrapper is provided if matplotlib is available.


def histogram_bins(data: Sequence[float], bins: int = 20) -> Tuple[List[float], List[int]]:
    """Compute histogram bins and counts (bin_edges, counts).

    Returns bin_edges (len bins+1) and counts (len bins).
    """
    if not data:
        return [0.0] * (bins + 1), [0] * bins
    lo = min(data)
    hi = max(data)
    if lo == hi:
        # degenerate: create small range around value
        lo = lo - 0.5
        hi = hi + 0.5
    width = (hi - lo) / bins
    edges = [lo + i * width for i in range(bins + 1)]
    counts = [0] * bins
    for x in data:
        # put x in appropriate bin, last edge inclusive
        if x == hi:
            counts[-1] += 1
        else:
            idx = int((x - lo) / width)
            if idx < 0:
                idx = 0
            elif idx >= bins:
                idx = bins - 1
            counts[idx] += 1
    return edges, counts


def coverage_to_plot(coverage: Sequence[int]) -> Tuple[List[int], List[int]]:
    """Return x (positions) and y (coverage) arrays for plotting."""
    return list(range(len(coverage))), list(coverage)


def simple_anomaly_score(ts: Sequence[float]) -> List[float]:
    """Compute a simple z-score based anomaly score for a timeseries.

    Returns list of z-scores same length as ts (0 for positions where stdev == 0).
    """
    if not ts:
        return []
    mean = sum(ts) / len(ts)
    var = sum((x - mean) ** 2 for x in ts) / len(ts)
    stdev = math.sqrt(var)
    if stdev == 0:
        return [0.0] * len(ts)
    return [(x - mean) / stdev for x in ts]


def ml_anomaly_wrapper(ts: Sequence[float], model_predict: Optional[Callable[[Sequence[float]], Sequence[float]]] = None) -> List[float]:
    """Run an ML model's predict callable on the timeseries to obtain anomaly scores.

    If model_predict is None, falls back to `simple_anomaly_score`.
    The model_predict callable should accept the full timeseries and return a list-like of scores same length.
    """
    if model_predict is None:
        return simple_anomaly_score(ts)
    scores = list(model_predict(ts))
    # ensure length matches
    if len(scores) != len(ts):
        raise ValueError("model_predict must return a score per input element")
    return scores


def try_plot_histogram(data: Sequence[float], bins: int = 20):
    """Produce a matplotlib Figure if matplotlib is available; otherwise return histogram data.

    Returns either (fig, ax) if plotting succeeded or (edges, counts) if matplotlib is unavailable.
    """
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return histogram_bins(data, bins=bins)
    edges, counts = histogram_bins(data, bins=bins)
    fig, ax = plt.subplots()
    ax.hist(data, bins=edges)
    ax.set_xlabel('Value')
    ax.set_ylabel('Count')
    ax.set_title('Histogram')
    return fig, ax


def save_figure(fig, path: str) -> None:
    try:
        fig.savefig(path)
    except Exception as e:
        # pass through to caller; tests won't call save by default
        raise
