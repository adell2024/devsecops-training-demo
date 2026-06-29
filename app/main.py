"""
Application FastAPI minimale - support d'entraînement DevSecOps.

Volontairement simple : l'objectif de ce projet n'est PAS la complexité
applicative, mais de servir de prétexte pour s'entraîner sur les
workflows Git / CI / CD / promotion d'artefacts.
"""

from fastapi import FastAPI

app = FastAPI(title="devsecops-training-demo")


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