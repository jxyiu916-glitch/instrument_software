"""ML hooks for trimming (thin wrappers)."""

from typing import Callable, Optional


def detect_adapter_with_model(seq: str, model_predict: Optional[Callable[[str], float]] = None, threshold: float = 0.5) -> bool:
    """Wrapper to detect adapters using a provided model callable.

    Kept separate so docs can reference `src/trim/ml.py` for ML hooks.
    """
    if model_predict is None:
        return False
    return float(model_predict(seq)) >= threshold
