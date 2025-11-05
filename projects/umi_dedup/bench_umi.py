import time

from umi.core import dedup_umis, unique_umi_fraction, dedup_umis_clustered


def bench():
    umis = ['AAA'] * 10000 + ['AAB'] * 3000 + ['AAC'] * 2000 + ['CCC'] * 5000
    t0 = time.time()
    _ = dedup_umis(umis)
    _ = unique_umi_fraction(umis)
    _ = dedup_umis_clustered(umis, max_distance=1)
    print('umi bench done', time.time() - t0)


if __name__ == '__main__':
    bench()
