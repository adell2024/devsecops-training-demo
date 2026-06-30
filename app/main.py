"""
Application FastAPI minimale - support d'entraînement DevSecOps.

Volontairement simple : l'objectif de ce projet n'est PAS la complexité
applicative, mais de servir de prétexte pour s'entraîner sur les
workflows Git / CI / CD / promotion d'artefacts.
"""

from fastapi import FastAPI
from app.metrics import metrics, metrics_middleware

app = FastAPI(title="devsecops-training-demo")
app.middleware("http")(metrics_middleware)


@app.get("/health")
def health() -> dict:
    """Endpoint de santé, utilisé par les tests et les futurs checks de déploiement."""
    return {"server status": "ok"}


@app.get("/version")
def version() -> dict:
    """
    Endpoint volontairement présent pour illustrer la traçabilité :
    en pratique, on pourrait injecter ici le tag/commit via une variable d'env
    positionnée au moment du build Docker (ex: APP_VERSION).
    """
    import os

    return {"version": os.getenv("APP_VERSION", "dev")}


@app.get("/info")
def info() -> dict:
    """Endpoint d'information sur l'application, utile pour le monitoring."""
    import os

    return {
        "app_name": "devsecops-training-demo",
        "status": "running",
        "version": os.getenv("APP_VERSION", "dev"),
    }


_request_count = 0


@app.get("/stats")
def stats() -> dict:
    """Retourne un compteur simple du nombre d'appels à cet endpoint."""
    global _request_count
    _request_count += 1
    return {"stats_calls": _request_count}


@app.get("/ping")
def ping() -> dict:
    """Endpoint minimal de test, pour valider rapidement le cycle CI/CD."""
    return {"pong": True}


@app.get("/about")
def about() -> dict:
    """Informations générales sur le projet."""
    return {
        "project": "devsecops-training-demo",
        "author": "adell2024",
        "description": "Projet d'entraînement DevSecOps",
    }


@app.get("/metrics")
def get_metrics() -> dict:
    """Endpoint de métriques : compteurs de requêtes par méthode/statut."""
    return {"metrics": metrics.get_all()}
