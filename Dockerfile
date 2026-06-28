FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# APP_VERSION est positionné au moment du build (--build-arg),
# puis exposé comme variable d'environnement pour l'endpoint /version.
# C'est un exemple simple de traçabilité "quelle version tourne réellement".
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
