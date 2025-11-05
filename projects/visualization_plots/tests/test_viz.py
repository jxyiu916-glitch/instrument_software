import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from viz.core import histogram_bins, coverage_to_plot, simple_anomaly_score, ml_anomaly_wrapper


def test_histogram_bins_basic():
    edges, counts = histogram_bins([1,2,3,4,5], bins=4)
    assert len(edges) == 5
    assert sum(counts) == 5


def test_coverage_plot():
    x, y = coverage_to_plot([10,20,30])
    assert x == [0,1,2]
    assert y == [10,20,30]


def test_anomaly_score_and_ml_wrapper():
    ts = [0,0,0,10,0]
    scores = simple_anomaly_score(ts)
    assert len(scores) == len(ts)
    # ml wrapper fallback
    s2 = ml_anomaly_wrapper(ts)
    assert s2 == scores
    # test ml callable with correct length
    def fake_model(t):
        return [float(x>5) for x in t]
    s3 = ml_anomaly_wrapper(ts, model_predict=fake_model)
    assert s3 == [0.0,0.0,0.0,1.0,0.0]
