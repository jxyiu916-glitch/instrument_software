import time
from alignment.core import mapping_rate, softclip_stats, insert_size_stats


def bench():
    records = []
    for i in range(10000):
        cigar = '5S95M' if i % 10 == 0 else '100M'
        records.append({'cigar': cigar, 'flag': 0})
    t0 = time.time()
    _ = mapping_rate(records)
    _ = softclip_stats(records)
    _ = insert_size_stats([100 + (i % 50) for i in range(10000)])
    print('alignment bench done', time.time() - t0)


if __name__ == '__main__':
    bench()
