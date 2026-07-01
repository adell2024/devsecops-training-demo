import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rate_limit import rate_limiter
from app.metrics import metrics


@pytest.fixture(autouse=True)
def reset_counters():
    """Réinitialise les compteurs avant CHAQUE test."""
    rate_limiter.reset()
    metrics.reset()


def test_rate_limit_headers_present() -> None:
    """Les headers X-RateLimit-* doivent être présents."""
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/ping")
    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert response.headers["X-RateLimit-Limit"] == "10"


def test_rate_limit_allows_under_limit() -> None:
    """10 requêtes doivent passer."""
    client = TestClient(app, raise_server_exceptions=False)
    for i in range(10):
        response = client.get("/ping")
        assert response.status_code == 200
        remaining = int(response.headers["X-RateLimit-Remaining"])
        assert remaining == 9 - i


def test_rate_limit_blocks_at_limit() -> None:
    """La 11ème requête doit être bloquée (429)."""
    client = TestClient(app, raise_server_exceptions=False)
    for _ in range(10):
        client.get("/ping")

    response = client.get("/ping")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]


def test_rate_limit_status_endpoint() -> None:
    """L'endpoint /rate-limit-status retourne les infos."""
    client = TestClient(app, raise_server_exceptions=False)
    client.get("/ping")
    response = client.get("/rate-limit-status")
    assert response.status_code == 200
    body = response.json()
    assert body["max_requests"] == 10
    # Le endpoint /rate-limit-status lui-même est comptabilisé
    assert body["current_count"] == 2  # /ping + /rate-limit-status


def test_rate_limit_reset() -> None:
    """Le reset fonctionne."""
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/rate-limit-status")
    # Le endpoint /rate-limit-status lui-même est comptabilisé
    assert response.json()["current_count"] == 1
