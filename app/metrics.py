"""
Middleware et endpoint de métriques simples (en mémoire).
En production, on utiliserait Prometheus/StatsD. Ici, c'est volontairement
minimal pour l'entraînement DevSecOps.
"""

from collections import defaultdict
from fastapi import Request, Response


class MetricsCollector:
    """Collecte les compteurs de requêtes en mémoire."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)

    def record(self, method: str, path: str, status_code: int) -> None:
        """Incrémente le compteur pour une combinaison méthode+statut."""
        key = f"{method}:{path}:{status_code}"
        self._counters[key] += 1

    def get_all(self) -> dict[str, int]:
        """Retourne une copie des compteurs."""
        return dict(self._counters)

    def reset(self) -> None:
        """Réinitialise les compteurs (utile pour les tests)."""
        self._counters.clear()


# Instance globale (volontairement simple pour ce training)
metrics = MetricsCollector()


async def metrics_middleware(request: Request, call_next) -> Response:
    """Middleware FastAPI qui enregistre chaque requête."""
    response = await call_next(request)
    metrics.record(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )
    return response
