from typing import Iterable, Dict, List, Tuple
import re
import statistics

# Simple helpers that operate on lightweight alignment-like records. For interview purposes we avoid
# parsing full BAM/SAM; instead these helpers accept iterables of small dicts or tuples with keys used below.


def mapping_rate(records: Iterable[Dict]) -> float:
    """Compute fraction of records that are mapped.

    Accepts records where a record is a dict with key 'flag' (int) or 'is_unmapped' (bool).
    """
    total = 0
    mapped = 0
    for r in records:
        total += 1
        is_unmapped = False
        if isinstance(r, dict):
            if 'is_unmapped' in r:
                is_unmapped = bool(r['is_unmapped'])
            elif 'flag' in r:
                # SAM flag 0x4 means unmapped
                is_unmapped = bool(int(r['flag']) & 0x4)
        else:
            # tuple expected: (qname, flag, rname, pos, mapq, cigar, seq)
            try:
                flag = int(r[1])
                is_unmapped = bool(flag & 0x4)
            except Exception:
                is_unmapped = False
        if not is_unmapped:
            mapped += 1
    return mapped / total if total > 0 else 0.0


_cigar_re = re.compile(r"(\d+)([MIDNSHP=X])")


def parse_cigar(cigar: str) -> List[Tuple[int, str]]:
    if not cigar:
        return []
    return [(int(length), op) for length, op in _cigar_re.findall(cigar)]


def softclip_lengths(cigar: str) -> Tuple[int, int]:
    """Return (left_softclip, right_softclip) lengths from a CIGAR string."""
    left = 0
    right = 0
    if not cigar:
        return left, right
    ops = parse_cigar(cigar)
    if ops and ops[0][1] == 'S':
        left = ops[0][0]
    if ops and ops[-1][1] == 'S':
        right = ops[-1][0]
    return left, right


def softclip_stats(records: Iterable[Dict]) -> Dict[str, float]:
    """Compute simple stats for soft-clipping: mean left, mean right, fraction clipped

    Expects records with a 'cigar' field (string) or tuple where cigar is element 5.
    """
    lefts = []
    rights = []
    n = 0
    clipped = 0
    for r in records:
        n += 1
        cigar = None
        if isinstance(r, dict) and 'cigar' in r:
            cigar = r['cigar']
        else:
            try:
                cigar = r[5]
            except Exception:
                cigar = ''
        l, rt = softclip_lengths(cigar)
        lefts.append(l)
        rights.append(rt)
        if l > 0 or rt > 0:
            clipped += 1
    return {
        'mean_left_softclip': statistics.mean(lefts) if lefts else 0.0,
        'mean_right_softclip': statistics.mean(rights) if rights else 0.0,
        'fraction_clipped': clipped / n if n > 0 else 0.0,
        'n_records': n,
    }


def insert_size_stats(tlens: Iterable[int]) -> Dict[str, float]:
    lst = list(tlens)
    if not lst:
        return {'mean': 0.0, 'median': 0.0, 'stdev': 0.0}
    return {'mean': statistics.mean(lst), 'median': statistics.median(lst), 'stdev': statistics.pstdev(lst)}


def flag_summary(records: Iterable[Dict]) -> Dict[str, int]:
    """Return counts for common SAM flag properties: paired, unmapped, reverse, secondary, duplicate."""
    summary = {'total': 0, 'paired': 0, 'unmapped': 0, 'reverse': 0, 'secondary': 0, 'duplicate': 0}
    for r in records:
        summary['total'] += 1
        flag = 0
        if isinstance(r, dict) and 'flag' in r:
            flag = int(r['flag'])
        else:
            try:
                flag = int(r[1])
            except Exception:
                flag = 0
        if flag & 0x1:
            summary['paired'] += 1
        if flag & 0x4:
            summary['unmapped'] += 1
        if flag & 0x10:
            summary['reverse'] += 1
        if flag & 0x100:
            summary['secondary'] += 1
        if flag & 0x400:
            summary['duplicate'] += 1
    return summary
