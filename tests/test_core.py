from src.app.core import process_records


def test_process_records_basic():
    records = [{"value": "A"}, {"value": "B"}, {"value": "A"}]
    out = process_records(records)
    assert out == {"A": 2, "B": 1}


def test_process_records_skips_missing():
    records = [{}, {"value": "A"}, {"value": None}, {"value": "A"}]
    out = process_records(records)
    assert out == {"A": 2}
