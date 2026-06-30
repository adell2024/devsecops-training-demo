from fastapi.testclient import TestClient

from app.main import app
from app.metrics import metrics

client = TestClient(app)


def test_metrics_endpoint_empty() -> None:
    """Au démarrage, les métriques sont vides."""
    metrics.reset()
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {"metrics": {}}


def test_metrics_records_request() -> None:
    """Une requête GET /health est comptabilisée."""
    metrics.reset()
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    assert "GET:/health:200" in body["metrics"]
    assert body["metrics"]["GET:/health:200"] == 1


def test_metrics_records_multiple_requests() -> None:
    """Plusieurs requêtes sur le même endpoint s'accumulent."""
    metrics.reset()
    client.get("/ping")
    client.get("/ping")
    client.get("/ping")
    response = client.get("/metrics")
    body = response.json()
    assert body["metrics"]["GET:/ping:200"] == 3


def test_metrics_records_different_status_codes() -> None:
    """Un 404 est aussi comptabilisé."""
    metrics.reset()
    client.get("/nonexistent")
    response = client.get("/metrics")
    body = response.json()
    assert "GET:/nonexistent:404" in body["metrics"]
    assert body["metrics"]["GET:/nonexistent:404"] == 1


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


def test_stats_increments() -> None:
    first = client.get("/stats").json()["stats_calls"]
    second = client.get("/stats").json()["stats_calls"]
    assert second == first + 1


def test_ping() -> None:
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"pong": True}


def test_about() -> None:
    response = client.get("/about")
    assert response.status_code == 200
    body = response.json()
    assert body["project"] == "devsecops-training-demo"
    assert body["author"] == "adell2024"
