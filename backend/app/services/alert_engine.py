"""Alert engine for anomaly detection and management."""

import logging
from typing import List

from sqlalchemy.orm import Session

from app.db.models import Alert

logger = logging.getLogger(__name__)


class AlertEngine:
    """Engine for managing alerts and anomalies."""

    @staticmethod
    def get_active_alerts(
        database: Session,
        aoi_id: int = None,
        alert_type: str = None,
        severity: str = None,
        limit: int = 50,
    ) -> List[Alert]:
        """
        Get active alerts with optional filtering.

        Args:
            database: Database session
            aoi_id: Optional AOI ID filter
            alert_type: Optional alert type filter
            severity: Optional severity filter
            limit: Maximum number of results

        Returns:
            List of alerts
        """
        query = database.query(Alert)

        if aoi_id:
            query = query.filter(Alert.aoi_id == aoi_id)
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        if severity:
            query = query.filter(Alert.severity == severity)

        return query.order_by(Alert.detected_at.desc()).limit(limit).all()

    @staticmethod
    def resolve_alert(database: Session, alert_id: int) -> Alert:
        """
        Mark alert as resolved.

        Args:
            database: Database session
            alert_id: Alert ID

        Returns:
            Updated alert
        """
        alert = database.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            # In a full implementation, you might add a 'resolved_at' field
            database.delete(alert)
            database.commit()
            logger.info(f"Alert {alert_id} resolved")
        return alert

    @staticmethod
    def create_custom_alert(
        database: Session,
        aoi_id: int,
        alert_type: str,
        severity: str,
        description: str,
        geometry: dict,
        satellite_source: str,
        confidence_score: float = 0.5,
    ) -> Alert:
        """
        Create a custom alert.

        Args:
            database: Database session
            aoi_id: AOI ID
            alert_type: Alert type
            severity: Severity level
            description: Alert description
            geometry: GeoJSON point geometry
            satellite_source: Data source
            confidence_score: Confidence score (0-1)

        Returns:
            Created alert
        """
        alert = Alert(
            aoi_id=aoi_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            geom=geometry,
            satellite_source=satellite_source,
            confidence_score=confidence_score,
        )
        database.add(alert)
        database.commit()
        logger.info(f"Custom alert created for AOI {aoi_id}")
        return alert
