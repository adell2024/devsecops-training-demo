"""
Middleware et endpoint de métriques simples (en mémoire).
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
        """Réinitialise les compteurs."""
        self._counters.clear()


metrics = MetricsCollector()


async def metrics_middleware(request: Request, call_next) -> Response:
    """Middleware FastAPI qui enregistre chaque requête."""
    try:
        response = await call_next(request)
        metrics.record(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response
    except Exception as e:
        # Enregistrer l'erreur même si le middleware suivant lève une exception
        status_code = getattr(e, "status_code", 500)
        metrics.record(
            method=request.method,
            path=request.url.path,
            status_code=status_code,
        )
        raise
