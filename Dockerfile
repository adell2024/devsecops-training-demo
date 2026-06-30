# =============================================================================
# Dockerfile durci — DevSecOps Training Demo
# =============================================================================
FROM python:3.12-bookworm AS builder
WORKDIR /build

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-bookworm
WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Créer l'utilisateur non-root AVANT de copier les fichiers,
# pour pouvoir lui en attribuer la propriété directement.
RUN groupadd -r appgroup && useradd -r -m -g appgroup appuser

# Copier les packages Python dans le HOME de appuser (pas /root),
# et lui en donner la propriété explicitement.
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

COPY --chown=appuser:appgroup app/ ./app/

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
