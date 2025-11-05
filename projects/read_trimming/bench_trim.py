import time
from trim.core import trim_adapter_exact, sliding_window_trim


def bench():
    seqs = ['ACGT' * 50 + 'AGATCGGAAGAGC' for _ in range(10000)]
    t0 = time.time()
    for s in seqs:
        _ = trim_adapter_exact(s, 'AGATCGGAAGAGC', max_mismatches=1)
        _ = sliding_window_trim(s, [30] * len(s), window=4, min_avg=20)
    print('trim bench done', time.time() - t0)


if __name__ == '__main__':
    bench()
