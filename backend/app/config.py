"""Configuration module for EcoSat Monitor application."""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # App
    APP_NAME: str = "EcoSat Monitor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://ecosat:ecosat@localhost:5432/ecosat"
    )
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Google Earth Engine
    GEE_PROJECT_ID: str = os.getenv("GEE_PROJECT_ID", "")
    GEE_SERVICE_ACCOUNT_JSON: Optional[str] = os.getenv("GEE_SERVICE_ACCOUNT_JSON")

    # NASA EarthData
    NASA_EARTHDATA_USER: str = os.getenv("NASA_EARTHDATA_USER", "")
    NASA_EARTHDATA_PASS: str = os.getenv("NASA_EARTHDATA_PASS", "")

    # Copernicus
    COPERNICUS_DSM_USER: str = os.getenv("COPERNICUS_DSM_USER", "")
    COPERNICUS_DSM_PASS: str = os.getenv("COPERNICUS_DSM_PASS", "")

    # Tile server
    TILE_STORAGE_PATH: str = os.getenv("TILE_STORAGE_PATH", "/data/tiles")
    TITILER_URL: Optional[str] = os.getenv("TITILER_URL")

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["*"]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
