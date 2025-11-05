from fastapi.testclient import TestClient
from src.api.server import app


def test_process_endpoint():
    client = TestClient(app)
    payload = [{"value": "A"}, {"value": "B"}, {"value": "A"}]
    r = client.post("/process", json=payload)
    assert r.status_code == 200
    assert r.json() == {"A": 2, "B": 1}


def test_process_endpoint_skips_missing():
    client = TestClient(app)
    payload = [{}, {"value": "A"}, {"value": None}, {"value": "A"}]
    r = client.post("/process", json=payload)
    assert r.status_code == 200
    assert r.json() == {"A": 2}
