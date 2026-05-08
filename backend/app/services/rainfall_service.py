"""Rainfall data service module."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

import ee
from sqlalchemy.orm import Session

from app.core import GEEClient, DataIngestionException
from app.db.models import TimeseriesStats, Alert

logger = logging.getLogger(__name__)


class RainfallService:
    """Service for handling rainfall data operations."""

    def __init__(self):
        """Initialize rainfall service."""
        self.gee_client = GEEClient()

    def ingest_rainfall_data(
        self,
        aoi: "AOI",  # type: ignore
        database: Session,
        start_date: str,
        end_date: str,
    ) -> Dict:
        """
        Ingest rainfall data for AOI.

        Args:
            aoi: Area of Interest object
            database: Database session
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Starting rainfall data ingestion for AOI {aoi.id}")

            # Convert geometry to ee.Geometry
            from shapely.geometry import shape

            geom_dict = shape(aoi.geom)
            ee_geometry = ee.Geometry.Polygon(
                [list(coords) for coords in geom_dict.exterior.coords]
            )

            # Get rainfall image from GEE
            rainfall_image = self.gee_client.get_rainfall(
                ee_geometry, start_date, end_date
            )

            if rainfall_image is None:
                raise DataIngestionException("No rainfall data available for date range")

            # Calculate statistics
            stats = self.gee_client.get_region_statistics(rainfall_image, ee_geometry)

            # Store in database
            ts_stat = TimeseriesStats(
                aoi_id=aoi.id,
                data_type="rainfall",
                date=end_date,
                mean_value=float(stats.get("mean", {}).get("precipitationCal", 0)),
                min_value=float(stats.get("min", {}).get("precipitationCal", 0)),
                max_value=float(stats.get("max", {}).get("precipitationCal", 0)),
                stddev_value=float(stats.get("stdDev", {}).get("precipitationCal", 0)),
                data_source="gpm",
            )
            database.add(ts_stat)

            # Detect anomalies (extreme rainfall)
            self._detect_rainfall_anomalies(aoi, database, ts_stat.mean_value)

            database.commit()

            logger.info(f"Successfully ingested rainfall data for AOI {aoi.id}")
            return {
                "status": "success",
                "aoi_id": aoi.id,
                "data_type": "rainfall",
                "mean_value": ts_stat.mean_value,
            }

        except Exception as e:
            logger.error(f"Failed to ingest rainfall data: {e}")
            raise DataIngestionException(f"Rainfall data ingestion failed: {e}")

    def _detect_rainfall_anomalies(
        self,
        aoi: "AOI",  # type: ignore
        database: Session,
        current_value: float,
    ) -> None:
        """
        Detect rainfall anomalies (flood risk).

        Args:
            aoi: Area of Interest
            database: Database session
            current_value: Current rainfall value
        """
        try:
            # Get 90-day baseline
            ninety_days_ago = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")

            baseline_stats = (
                database.query(TimeseriesStats)
                .filter(
                    TimeseriesStats.aoi_id == aoi.id,
                    TimeseriesStats.data_type == "rainfall",
                    TimeseriesStats.date >= ninety_days_ago,
                )
                .all()
            )

            if not baseline_stats:
                return

            # Calculate 95th percentile
            values = sorted([s.mean_value for s in baseline_stats if s.mean_value])
            if not values:
                return

            percentile_95 = values[int(len(values) * 0.95)]

            # Detect extreme rainfall (> 95th percentile)
            if current_value > percentile_95:
                severity = "critical" if current_value > percentile_95 * 1.5 else "high"
                alert = Alert(
                    aoi_id=aoi.id,
                    alert_type="flood_risk",
                    severity=severity,
                    description=f"Extreme rainfall detected: {current_value:.2f}mm (95th percentile: {percentile_95:.2f}mm)",
                    detected_at=datetime.utcnow(),
                    satellite_source="gpm",
                    confidence_score=0.80,
                    geom=aoi.geom,
                )
                database.add(alert)
                database.commit()
                logger.info(f"Flood risk alert created for AOI {aoi.id}")

        except Exception as e:
            logger.error(f"Failed to detect rainfall anomalies: {e}")

    def get_rainfall_timeseries(
        self,
        aoi_id: int,
        database: Session,
        start_date: str,
        end_date: str,
    ) -> List[TimeseriesStats]:
        """
        Get rainfall time-series data.

        Args:
            aoi_id: AOI ID
            database: Database session
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of TimeseriesStats objects
        """
        return (
            database.query(TimeseriesStats)
            .filter(
                TimeseriesStats.aoi_id == aoi_id,
                TimeseriesStats.data_type == "rainfall",
                TimeseriesStats.date >= start_date,
                TimeseriesStats.date <= end_date,
            )
            .order_by(TimeseriesStats.date)
            .all()
        )
