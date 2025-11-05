import time
from molecule.core import count_molecules, collapse_umis_by_count


def bench():
    records = []
    for g in range(1000):
        gene = f'G{g}'
        for u in range(10):
            umi = f'U{u}'
            # add some reads per UMI
            for r in range(u+1):
                records.append((gene, umi))
    t0 = time.time()
    _ = count_molecules(records)
    _ = collapse_umis_by_count(records, min_reads=3)
    print('molecule bench done', time.time() - t0)


if __name__ == '__main__':
    bench()
