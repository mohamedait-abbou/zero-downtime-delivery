from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready():
    assert client.get("/ready").json() == {"ready": True}


def test_work_ok():
    body = client.get("/work", params={"n": 5}).json()
    assert body["processed"] == 5
    assert body["version"] == "dev"


def test_work_rejects_zero():
    assert client.get("/work", params={"n": 0}).status_code == 400
