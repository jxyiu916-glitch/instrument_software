"""Small, dependency-free SAM record parsing utilities.

These helpers are intentionally lightweight and do not replace full BAM/SAM
parsers (such as pysam). They support the subset of fields used in the
alignment QC tests and pipelines.
"""
from typing import Iterator, Dict, List, Tuple, Optional


def _parse_flag(flag_field: str) -> int:
    try:
        return int(flag_field)
    except Exception:
        return 0


def parse_cigar(cigar: str) -> List[Tuple[int, str]]:
    """Parse a CIGAR string into a list of (length, op) tuples.

    Example: '10M1I5M' -> [(10,'M'), (1,'I'), (5,'M')]
    """
    import re

    parts = re.findall(r"(\d+)([MIDNSHP=X])", cigar)
    return [(int(l), op) for l, op in parts]


def parse_sam_records(lines: Iterator[str]) -> Iterator[Dict[str, Optional[str]]]:
    """Yield parsed SAM records as dicts for essential fields.

    Fields included: qname, flag (int), rname, pos (int), mapq (int), cigar, seq
    Lines starting with @ are skipped.
    """
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith("@"):
            continue
        fields = ln.split("\t")
        qname = fields[0]
        flag = _parse_flag(fields[1]) if len(fields) > 1 else 0
        rname = fields[2] if len(fields) > 2 else "*"
        pos = int(fields[3]) - 1 if len(fields) > 3 and fields[3].isdigit() else None
        mapq = int(fields[4]) if len(fields) > 4 and fields[4].isdigit() else None
        cigar = fields[5] if len(fields) > 5 else "*"
        seq = fields[9] if len(fields) > 9 else ""
        yield {
            "qname": qname,
            "flag": flag,
            "rname": rname,
            "pos": pos,
            "mapq": mapq,
            "cigar": cigar,
            "seq": seq,
        }


def get_read_length_from_cigar(cigar: str) -> int:
    """Return reference-consuming length of read from CIGAR (M, D, =, X, N)."""
    ops = parse_cigar(cigar)
    consume = set("MD=XN")
    total = 0
    for l, op in ops:
        if op in consume:
            total += l
    return total
