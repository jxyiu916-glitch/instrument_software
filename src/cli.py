"""Small CLI entrypoint for the scaffold.

Usage:
    python -m src.cli path/to/input.json

Input format: JSON array of objects with a `value` key, e.g.:
    [{"value": "A"}, {"value": "B"}, {"value": "A"}]

Output: JSON mapping values to counts printed to stdout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

from app.core import process_records


def load_json(path: Path) -> List[dict]:
    with path.open() as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Input JSON must be an array of objects")
    return data


def main(argv: List[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if not argv:
        print("Usage: python -m src.cli path/to/input.json", file=sys.stderr)
        return 2
    p = Path(argv[0])
    data = load_json(p)
    result = process_records(data)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
