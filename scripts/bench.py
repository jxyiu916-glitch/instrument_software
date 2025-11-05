"""Very small benchmark helper for micro-benchmarks."""
import json
import timeit
from pathlib import Path

from app.core import process_records


def run_once(path: Path):
    data = json.loads(path.read_text())
    process_records(data)


if __name__ == "__main__":
    path = Path("data/example_small.json")
    t = timeit.timeit(lambda: run_once(path), number=1000)
    print(f"1000 runs took {t:.4f}s")
