import time
from seqqc.core import basic_qc_stats, gc_content, length_histogram


def bench():
    seqs = ['ACTG' * 25 for _ in range(10000)]
    t0 = time.time()
    _ = basic_qc_stats(seqs)
    _ = gc_content(seqs)
    _ = length_histogram(seqs)
    print('seqqc bench done', time.time() - t0)


if __name__ == '__main__':
    bench()
