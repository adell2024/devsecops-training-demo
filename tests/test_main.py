from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"server status": "ok"}


def test_version_default() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_info() -> None:
    response = client.get("/info")
    assert response.status_code == 200
    body = response.json()
    assert body["app_name"] == "devsecops-training-demo"
    assert body["status"] == "running"