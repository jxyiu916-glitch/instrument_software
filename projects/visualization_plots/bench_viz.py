import time
from viz.core import histogram_bins, simple_anomaly_score


def bench():
    data = [i % 50 for i in range(100000)]
    t0 = time.time()
    _ = histogram_bins(data, bins=50)
    _ = simple_anomaly_score(data)
    print('viz bench done', time.time() - t0)


if __name__ == '__main__':
    bench()
