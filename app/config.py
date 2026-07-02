"""
Configuration de l'application exposée via endpoint.
En production, certaines valeurs viendraient de variables d'environnement.
"""

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Configuration immuable de l'application."""

    version: str
    environment: str
    debug: bool
    features: dict[str, bool]


def get_config() -> AppConfig:
    """Construit la configuration depuis l'environnement."""
    return AppConfig(
        version=os.getenv("APP_VERSION", "dev"),
        environment=os.getenv("APP_ENV", "development"),
        debug=os.getenv("APP_DEBUG", "false").lower() == "true",
        features={
            "metrics": True,
            "rate_limiting": True,
            "health_check": True,
        },
    )
