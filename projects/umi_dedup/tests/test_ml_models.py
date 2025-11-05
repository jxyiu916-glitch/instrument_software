import numpy as np
import pytest

from umi.ml_models import UMIErrorPredictor


def test_predictor_fallback():
    model = UMIErrorPredictor()
    X = [[1, 0, 30], [10, 1, 20]]
    probs = model.predict_proba(X)
    assert probs.shape == (2, 2)
    assert (probs >= 0).all() and (probs <= 1).all()


def test_fit_predict():
    model = UMIErrorPredictor()
    # small synthetic dataset
    X = [[1, 0, 30], [2, 1, 25], [10, 2, 15], [1, 1, 10]]
    y = [0, 0, 1, 1]
    try:
        model.fit(X, y)
        probs = model.predict_proba(X)
        assert probs.shape[0] == len(X)
    except RuntimeError:
        # sklearn may not be available in CI; in that case the test should skip
        pytest.skip("scikit-learn not installed in this environment")
