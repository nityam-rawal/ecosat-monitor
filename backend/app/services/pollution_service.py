"""Pollution data service module."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import ee
from sqlalchemy.orm import Session

from app.core import GEEClient, DataIngestionException
from app.db.models import TimeseriesStats, Alert, IngestionLog
from app.models.schemas import DataType, DataSource, AlertType, AlertSeverity

logger = logging.getLogger(__name__)


class PollutionService:
    """Service for handling pollution data operations."""

    def __init__(self):
        """Initialize pollution service."""
        self.gee_client = GEEClient()

    def ingest_pollution_data(
        self,
        aoi: "AOI",  # type: ignore
        database: Session,
        start_date: str,
        end_date: str,
        pollutant: str = "NO2",
    ) -> Dict:
        """
        Ingest pollution data for AOI.

        Args:
            aoi: Area of Interest object
            database: Database session
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            pollutant: Pollutant type (NO2, SO2, CO, O3, CH4)

        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Starting {pollutant} data ingestion for AOI {aoi.id}")

            # Create ingestion log entry
            ingest_log = IngestionLog(
                data_type=f"{pollutant.lower()}",
                source="sentinel-5p",
                date_range_start=start_date,
                date_range_end=end_date,
                status="processing",
            )
            database.add(ingest_log)
            database.commit()

            # Convert geometry to ee.Geometry
            from shapely.geometry import shape

            geom_dict = shape(aoi.geom)
            ee_geometry = ee.Geometry.Polygon(
                [list(coords) for coords in geom_dict.exterior.coords]
            )

            # Get pollution image from GEE
            pollution_image = self.gee_client.get_pollution(
                ee_geometry, start_date, end_date, pollutant
            )

            if pollution_image is None:
                raise DataIngestionException(f"No {pollutant} data available for date range")

            # Calculate statistics
            stats = self.gee_client.get_region_statistics(pollution_image, ee_geometry)

            # Store in database
            ts_stat = TimeseriesStats(
                aoi_id=aoi.id,
                data_type=pollutant.lower(),
                date=end_date,
                mean_value=float(stats.get("mean", {}).get(f"{pollutant}_column_number_density", 0)),
                min_value=float(stats.get("min", {}).get(f"{pollutant}_column_number_density", 0)),
                max_value=float(stats.get("max", {}).get(f"{pollutant}_column_number_density", 0)),
                stddev_value=float(stats.get("stdDev", {}).get(f"{pollutant}_column_number_density", 0)),
                data_source="sentinel-5p",
            )
            database.add(ts_stat)

            # Detect anomalies
            self._detect_pollution_anomalies(
                aoi, database, ts_stat.mean_value, pollutant
            )

            # Update ingestion log
            ingest_log.status = "completed"
            ingest_log.records_processed = 1
            ingest_log.completed_at = datetime.utcnow()
            database.commit()

            logger.info(f"Successfully ingested {pollutant} data for AOI {aoi.id}")
            return {
                "status": "success",
                "aoi_id": aoi.id,
                "data_type": pollutant,
                "mean_value": ts_stat.mean_value,
            }

        except Exception as e:
            logger.error(f"Failed to ingest {pollutant} data: {e}")
            ingest_log.status = "failed"
            ingest_log.error_message = str(e)
            ingest_log.completed_at = datetime.utcnow()
            database.commit()
            raise DataIngestionException(f"Pollution data ingestion failed: {e}")

    def _detect_pollution_anomalies(
        self,
        aoi: "AOI",  # type: ignore
        database: Session,
        current_value: float,
        pollutant: str,
    ) -> None:
        """
        Detect pollution anomalies.

        Args:
            aoi: Area of Interest
            database: Database session
            current_value: Current pollution value
            pollutant: Pollutant type
        """
        try:
            # Get 30-day baseline (simplified: use mean of last 30 days)
            thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

            baseline_stats = (
                database.query(TimeseriesStats)
                .filter(
                    TimeseriesStats.aoi_id == aoi.id,
                    TimeseriesStats.data_type == pollutant.lower(),
                    TimeseriesStats.date >= thirty_days_ago,
                )
                .all()
            )

            if not baseline_stats:
                logger.info(f"Insufficient baseline data for {pollutant} anomaly detection")
                return

            # Calculate mean and std dev
            values = [s.mean_value for s in baseline_stats if s.mean_value]
            if not values:
                return

            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            stddev = variance ** 0.5

            # Detect anomaly (> 2 standard deviations)
            if current_value > mean + (2 * stddev):
                alert = Alert(
                    aoi_id=aoi.id,
                    alert_type="pollution_spike",
                    severity="high" if current_value > mean + (3 * stddev) else "medium",
                    description=f"{pollutant} spike detected: {current_value:.2f} (baseline: {mean:.2f})",
                    detected_at=datetime.utcnow(),
                    satellite_source="sentinel-5p",
                    confidence_score=0.85,
                    geom=aoi.geom,
                )
                database.add(alert)
                database.commit()
                logger.info(f"Pollution alert created for {pollutant} in AOI {aoi.id}")

        except Exception as e:
            logger.error(f"Failed to detect pollution anomalies: {e}")

    def get_pollution_timeseries(
        self,
        aoi_id: int,
        database: Session,
        start_date: str,
        end_date: str,
        pollutant: str = "NO2",
    ) -> List[TimeseriesStats]:
        """
        Get pollution time-series data.

        Args:
            aoi_id: AOI ID
            database: Database session
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            pollutant: Pollutant type

        Returns:
            List of TimeseriesStats objects
        """
        return (
            database.query(TimeseriesStats)
            .filter(
                TimeseriesStats.aoi_id == aoi_id,
                TimeseriesStats.data_type == pollutant.lower(),
                TimeseriesStats.date >= start_date,
                TimeseriesStats.date <= end_date,
            )
            .order_by(TimeseriesStats.date)
            .all()
        )
