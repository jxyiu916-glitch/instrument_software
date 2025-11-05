"""Fleet telemetry utilities.

This module provides a lightweight, in-process telemetry recorder and
aggregator suitable for local testing and small deployments. The API is
dependency-free and exposes a pluggable backend hook for production
integration (e.g., StatsD, Prometheus, or an HTTP collector).
"""
from typing import Dict, Any, Callable, Optional
import threading
import time


class InMemoryTelemetry:
    """Thread-safe in-memory telemetry collector.

    Usage:
      collector = InMemoryTelemetry()
      collector.record_event("heartbeat", {"cpu": 0.5})
      summary = collector.aggregate()
    """

    def __init__(self, backend: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        self._lock = threading.Lock()
        self._events = []  # list of (timestamp, name, payload)
        self._backend = backend

    def record_event(self, name: str, payload: Dict[str, Any]) -> None:
        """Record an event. If backend is set, forward immediately."""
        ts = time.time()
        if self._backend is not None:
            try:
                self._backend(name, payload)
            except Exception:
                # Backend errors must not crash telemetry collection
                pass
        with self._lock:
            self._events.append((ts, name, dict(payload)))

    def aggregate(self) -> Dict[str, Dict[str, float]]:
        """Aggregate numeric metrics across recorded events.

        Returns a mapping metric -> {mean, min, max, count} aggregated across
        all recorded events with numeric values.
        """
        stats: Dict[str, Dict[str, float]] = {}
        with self._lock:
            events = list(self._events)
        numeric_acc: Dict[str, list] = {}
        for _, _, payload in events:
            for k, v in payload.items():
                if isinstance(v, (int, float)):
                    numeric_acc.setdefault(k, []).append(float(v))

        for k, vals in numeric_acc.items():
            if not vals:
                continue
            stats[k] = {
                "mean": sum(vals) / len(vals),
                "min": min(vals),
                "max": max(vals),
                "count": float(len(vals)),
            }
        return stats


def aggregate_metrics(metrics: Dict[str, float]) -> Dict[str, float]:
    """Simple stateless aggregator (helper) returning the same mapping.

    Kept for backwards-compatibility with older callers that expect a function
    with this signature.
    """
    return dict(metrics)


# Module-level default collector for convenience
_default_collector: Optional[InMemoryTelemetry] = None


def default_collector() -> InMemoryTelemetry:
    global _default_collector
    if _default_collector is None:
        _default_collector = InMemoryTelemetry()
    return _default_collector


def record_event(name: str, payload: Dict[str, Any]) -> None:
    """Convenience wrapper: record to the default in-memory collector."""
    default_collector().record_event(name, payload)

