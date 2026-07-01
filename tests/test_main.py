import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.metrics import metrics
from app.rate_limit import rate_limiter


@pytest.fixture(autouse=True)
def reset_counters():
    """Réinitialise les compteurs avant CHAQUE test."""
    metrics.reset()
    rate_limiter.reset()


def test_metrics_endpoint_empty() -> None:
    """Au démarrage, les métriques sont vides."""
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {"metrics": {}}


def test_metrics_records_request() -> None:
    """Une requête GET /health est comptabilisée."""
    client = TestClient(app)
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    assert "GET:/health:200" in body["metrics"]
    assert body["metrics"]["GET:/health:200"] == 1


def test_metrics_records_multiple_requests() -> None:
    """Plusieurs requêtes sur le même endpoint s'accumulent."""
    client = TestClient(app)
    client.get("/ping")
    client.get("/ping")
    client.get("/ping")
    response = client.get("/metrics")
    body = response.json()
    assert body["metrics"]["GET:/ping:200"] == 3


def test_metrics_records_different_status_codes() -> None:
    """Un 404 est aussi comptabilisé."""
    client = TestClient(app)
    client.get("/nonexistent")
    response = client.get("/metrics")
    body = response.json()
    assert "GET:/nonexistent:404" in body["metrics"]
    assert body["metrics"]["GET:/nonexistent:404"] == 1


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"server status": "ok"}


def test_version_default() -> None:
    client = TestClient(app)
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_info() -> None:
    client = TestClient(app)
    response = client.get("/info")
    assert response.status_code == 200
    body = response.json()
    assert body["app_name"] == "devsecops-training-demo"
    assert body["status"] == "running"


def test_stats_increments() -> None:
    client = TestClient(app)
    first = client.get("/stats").json()["stats_calls"]
    second = client.get("/stats").json()["stats_calls"]
    assert second == first + 1


def test_ping() -> None:
    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"pong": True}


def test_about() -> None:
    client = TestClient(app)
    response = client.get("/about")
    assert response.status_code == 200
    body = response.json()
    assert body["project"] == "devsecops-training-demo"
    assert body["author"] == "adell2024"
