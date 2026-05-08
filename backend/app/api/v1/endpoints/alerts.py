"""Alert management endpoints."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models import Alert as AlertModel
from app.db.session import get_session
from app.models.schemas import Alert, AlertCreate
from app.services import AlertEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[Alert])
async def get_alerts(
    aoi_id: Optional[int] = Query(None, description="Filter by AOI ID"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=500, description="Result limit"),
    db: Session = Depends(get_session),
) -> List[Alert]:
    """
    Get active alerts with optional filtering.

    Args:
        aoi_id: Optional AOI ID filter
        alert_type: Optional alert type filter
        severity: Optional severity filter
        limit: Maximum results
        db: Database session

    Returns:
        List of alerts
    """
    try:
        alerts = AlertEngine.get_active_alerts(
            db, aoi_id=aoi_id, alert_type=alert_type, severity=severity, limit=limit
        )
        return [Alert.from_orm(alert) for alert in alerts]
    except Exception as e:
        logger.error(f"Failed to fetch alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alerts",
        )


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(alert_id: int, db: Session = Depends(get_session)) -> Alert:
    """
    Get a specific alert.

    Args:
        alert_id: Alert ID
        db: Database session

    Returns:
        Alert object

    Raises:
        HTTPException: If alert not found
    """
    alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    return Alert.from_orm(alert)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def resolve_alert(alert_id: int, db: Session = Depends(get_session)) -> None:
    """
    Resolve (delete) an alert.

    Args:
        alert_id: Alert ID
        db: Database session

    Raises:
        HTTPException: If alert not found
    """
    try:
        AlertEngine.resolve_alert(db, alert_id)
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert",
        )
