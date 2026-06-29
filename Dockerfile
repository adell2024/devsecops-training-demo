# =============================================================================
# Dockerfile durci — DevSecOps Training Demo
# =============================================================================
# Objectifs :
#   1. Surface d'attaque minimale (multi-stage, non-root)
#   2. Packages OS à jour (apt-get upgrade) pour passer Trivy
#   3. Traçabilité build-arg → runtime (endpoint /version)
#   4. Pas de secrets, pas de cache pip, pas de dev tools en runtime
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 : Builder — compile & installe les dépendances Python
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Mettre à jour les packages système ET installer les outils de compilation
# nécessaires pour les packages Python sans wheel (ex: certaines libs C).
RUN apt-get update &&     apt-get upgrade -y &&     apt-get install -y --no-install-recommends gcc libc6-dev &&     apt-get clean &&     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Installer les dépendances dans un répertoire isolé (--user)
# pour pouvoir les copier ensuite dans l'image runtime.
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 : Runtime — image finale minimaliste & sécurisée
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# 1. Mettre à jour les packages OS de base (CRITIQUE pour Trivy)
#    Cela patche libc, openssl, zlib, etc. contre les CVEs connues.
RUN apt-get update &&     apt-get upgrade -y &&     apt-get install -y --no-install-recommends &&     apt-get clean &&     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 2. Copier les packages Python installés depuis le builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 3. Copier l'application (uniquement le code nécessaire)
COPY app/ ./app/

# 4. Traçabilité : la version est injectée au build (--build-arg)
#    et exposée au runtime pour l'endpoint /version.
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

# 5. Créer un utilisateur non-root pour le runtime
#    (évite l'exécution en root dans le conteneur)
RUN groupadd -r appgroup && useradd -r -g appgroup appuser &&     chown -R appuser:appgroup /app
USER appuser

# 6. Exposer le port de l'application
EXPOSE 8000

# 7. Healthcheck natif Docker (optionnel mais recommandé)
#    Adapte l'URL selon ton endpoint de santé réel.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3     CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 8. Lancer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
