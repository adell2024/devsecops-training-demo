"""
Middleware combiné : métriques + rate limiting.
"""

from fastapi import Request, Response
from starlette.responses import JSONResponse
from app.metrics import metrics
from app.rate_limit import rate_limiter


async def combined_middleware(request: Request, call_next) -> Response:
    """Middleware unique : rate limit + métriques."""
    # --- Rate Limiting ---
    client_ip = request.headers.get(
        "x-forwarded-for", request.client.host if request.client else "unknown"
    )
    client_ip = client_ip.split(",")[0].strip()

    allowed, remaining, reset_in = rate_limiter.is_allowed(client_ip)

    # BLOQUER AVANT d'appeler le endpoint
    if not allowed:
        # Enregistrer le blocage dans les métriques
        metrics.record(
            method=request.method,
            path=request.url.path,
            status_code=429,
        )
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded. Retry in {reset_in} seconds."},
            headers={
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_in),
            },
        )

    # --- Appel suivant ---
    response = await call_next(request)

    # --- Métriques (succès) ---
    metrics.record(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )

    # --- Headers Rate Limit (succès) ---
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_in)

    return response
