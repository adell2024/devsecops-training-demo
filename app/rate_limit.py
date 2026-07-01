"""
Rate limiting simple en mémoire (fenêtre glissante de 60 secondes).
En production, on utiliserait Redis. Ici, c'est volontairement minimal.
"""

import time
from collections import defaultdict
from fastapi import Request, Response, HTTPException


class RateLimiter:
    """Limite les requêtes par IP : 10 req/minute."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # ip -> liste des timestamps de requêtes
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> tuple[bool, int, int]:
        """
        Vérifie si une requête est autorisée.
        Retourne : (autorisé, remaining, reset_in)
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Nettoyer les anciennes requêtes
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > window_start
        ]

        current_count = len(self._requests[client_ip])

        if current_count >= self.max_requests:
            reset_in = int(self._requests[client_ip][0] + self.window_seconds - now) + 1
            return False, 0, reset_in

        self._requests[client_ip].append(now)
        remaining = self.max_requests - current_count - 1
        reset_in = self.window_seconds
        return True, remaining, reset_in

    def reset(self) -> None:
        """Réinitialise tous les compteurs (utile pour les tests)."""
        self._requests.clear()


# Instance globale
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


async def rate_limit_middleware(request: Request, call_next) -> Response:
    """Middleware qui applique le rate limiting."""
    client_ip = request.headers.get(
        "x-forwarded-for", request.client.host if request.client else "unknown"
    )
    client_ip = client_ip.split(",")[0].strip()

    allowed, remaining, reset_in = rate_limiter.is_allowed(client_ip)

    response = await call_next(request)

    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_in)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Retry in {reset_in} seconds.",
        )

    return response
