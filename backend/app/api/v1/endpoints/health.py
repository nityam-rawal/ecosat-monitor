"""Health check endpoint."""

import logging
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_session
from app.models.schemas import HealthCheck

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_session)) -> Dict:
    """
    Health check endpoint.

    Returns:
        Health status with component status
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    # Cache status (simplified - would check Redis in production)
    cache_status = "healthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.APP_VERSION,
        "database": db_status,
        "cache": cache_status,
    }
