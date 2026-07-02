from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_config_endpoint_exists() -> None:
    """L'endpoint /config doit exister et retourner 200."""
    response = client.get("/config")
    assert response.status_code == 200


def test_config_has_required_fields() -> None:
    """La réponse doit contenir les champs obligatoires."""
    response = client.get("/config")
    body = response.json()
    assert "version" in body
    assert "environment" in body
    assert "debug" in body
    assert "features" in body


def test_config_features_is_dict() -> None:
    """Les features doivent être un dictionnaire de booléens."""
    response = client.get("/config")
    features = response.json()["features"]
    assert isinstance(features, dict)
    for key, value in features.items():
        assert isinstance(value, bool)


def test_config_version_default() -> None:
    """Sans variable d'env, la version par défaut est 'dev'."""
    response = client.get("/config")
    assert response.json()["version"] == "dev"


def test_config_environment_default() -> None:
    """Sans variable d'env, l'environnement par défaut est 'development'."""
    response = client.get("/config")
    assert response.json()["environment"] == "development"


def test_config_debug_default() -> None:
    """Sans variable d'env, debug est False par défaut."""
    response = client.get("/config")
    assert response.json()["debug"] is False
