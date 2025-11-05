import time
from barcode.core import build_whitelist, correct_barcode, barcode_counts


def bench():
    whitelist = [f'BC{str(i).zfill(4)}' for i in range(1000)]
    wl = build_whitelist(whitelist)
    barcodes = [whitelist[i % 1000] for i in range(20000)]
    # introduce some errors
    barcodes[5] = 'BC000X'
    start = time.time()
    _ = barcode_counts(barcodes)
    _ = correct_barcode('BC000X', wl, max_distance=1)
    print('barcode bench done', time.time() - start)


if __name__ == '__main__':
    bench()
