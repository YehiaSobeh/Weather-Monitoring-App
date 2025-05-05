from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
API = "/api/v1"


def test_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
