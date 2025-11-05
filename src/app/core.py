from typing import Iterable, Dict


def process_records(records: Iterable[dict]) -> Dict[str, int]:
    """Simple example processor for interview practice.

    Counts occurrences of the "value" field in input records.

    Args:
        records: iterable of dicts, each with a 'value' key (string).

    Returns:
        A dict mapping value -> count.
    """
    counts: Dict[str, int] = {}
    for r in records:
        v = r.get("value")
        if v is None:
            # skip malformed/empty records
            continue
        counts[v] = counts.get(v, 0) + 1
    return counts
