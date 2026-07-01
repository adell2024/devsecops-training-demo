"""
Application FastAPI minimale - support d'entraînement DevSecOps.
"""

import time
from fastapi import FastAPI, Request
from app.middleware import combined_middleware

app = FastAPI(title="devsecops-training-demo")
app.middleware("http")(combined_middleware)


@app.get("/health")
def health() -> dict:
    """Endpoint de santé."""
    return {"server status": "ok"}


@app.get("/version")
def version() -> dict:
    """Traçabilité : version injectée au build."""
    import os

    return {"version": os.getenv("APP_VERSION", "dev")}


@app.get("/info")
def info() -> dict:
    """Informations sur l'application."""
    import os

    return {
        "app_name": "devsecops-training-demo",
        "status": "running",
        "version": os.getenv("APP_VERSION", "dev"),
    }


_request_count = 0


@app.get("/stats")
def stats() -> dict:
    """Compteur d'appels."""
    global _request_count
    _request_count += 1
    return {"stats_calls": _request_count}


@app.get("/ping")
def ping() -> dict:
    """Endpoint minimal de test."""
    return {"pong": True}


@app.get("/about")
def about() -> dict:
    """Informations générales."""
    return {
        "project": "devsecops-training-demo",
        "author": "adell2024",
        "description": "Projet d'entraînement DevSecOps",
    }


@app.get("/metrics")
def get_metrics() -> dict:
    """Compteurs de requêtes."""
    from app.metrics import metrics

    return {"metrics": metrics.get_all()}


@app.get("/rate-limit-status")
def rate_limit_status(request: Request) -> dict:
    """État du rate limiter pour cette IP."""
    from app.rate_limit import rate_limiter

    client_ip = request.headers.get(
        "x-forwarded-for", request.client.host if request.client else "unknown"
    )
    client_ip = client_ip.split(",")[0].strip()

    now = time.time()
    window_start = now - rate_limiter.window_seconds
    recent = [
        ts for ts in rate_limiter._requests.get(client_ip, []) if ts > window_start
    ]

    return {
        "client_ip": client_ip,
        "max_requests": rate_limiter.max_requests,
        "current_count": len(recent),
        "window_seconds": rate_limiter.window_seconds,
    }
