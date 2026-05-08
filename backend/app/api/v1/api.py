"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1.endpoints import aois, alerts, datasets, export, health, timeseries, tiles

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router)
api_router.include_router(datasets.router)
api_router.include_router(aois.router)
api_router.include_router(timeseries.router)
api_router.include_router(alerts.router)
api_router.include_router(tiles.router)
api_router.include_router(export.router)
