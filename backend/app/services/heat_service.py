"""Heat data service module."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

import ee
from sqlalchemy.orm import Session

from app.core import GEEClient, DataIngestionException
from app.db.models import TimeseriesStats, Alert

logger = logging.getLogger(__name__)


class HeatService:
    """Service for handling land surface temperature and heat data."""

    def __init__(self):
        """Initialize heat service."""
        self.gee_client = GEEClient()

    def ingest_heat_data(
        self,
        aoi: "AOI",  # type: ignore
        database: Session,
        start_date: str,
        end_date: str,
    ) -> Dict:
        """
        Ingest LST (Land Surface Temperature) data for AOI.

        Args:
            aoi: Area of Interest object
            database: Database session
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Starting LST data ingestion for AOI {aoi.id}")

            # Convert geometry to ee.Geometry
            from shapely.geometry import shape

            geom_dict = shape(aoi.geom)
            ee_geometry = ee.Geometry.Polygon(
                [list(coords) for coords in geom_dict.exterior.coords]
            )

            # Get LST image from GEE
            lst_image = self.gee_client.get_lst(ee_geometry, start_date, end_date)

            if lst_image is None:
                raise DataIngestionException("No LST data available for date range")

            # Calculate statistics
            stats = self.gee_client.get_region_statistics(lst_image, ee_geometry)

            # Store in database
            ts_stat = TimeseriesStats(
                aoi_id=aoi.id,
                data_type="lst",
                date=end_date,
                mean_value=float(stats.get("mean", {}).get("LST_C", 0)),
                min_value=float(stats.get("min", {}).get("LST_C", 0)),
                max_value=float(stats.get("max", {}).get("LST_C", 0)),
                stddev_value=float(stats.get("stdDev", {}).get("LST_C", 0)),
                data_source="modis",
            )
            database.add(ts_stat)

            # Detect anomalies (heat waves)
            self._detect_heat_wave_anomalies(aoi, database, ts_stat.mean_value)

            database.commit()

            logger.info(f"Successfully ingested LST data for AOI {aoi.id}")
            return {
                "status": "success",
                "aoi_id": aoi.id,
                "data_type": "lst",
                "mean_value": ts_stat.mean_value,
            }

        except Exception as e:
            logger.error(f"Failed to ingest LST data: {e}")
            raise DataIngestionException(f"LST data ingestion failed: {e}")

    def _detect_heat_wave_anomalies(
        self,
        aoi: "AOI",  # type: ignore
        database: Session,
        current_temp: float,
    ) -> None:
        """
        Detect heat wave anomalies (high temperature).

        Args:
            aoi: Area of Interest
            database: Database session
            current_temp: Current temperature in Celsius
        """
        try:
            # Get 30-day baseline
            thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

            baseline_stats = (
                database.query(TimeseriesStats)
                .filter(
                    TimeseriesStats.aoi_id == aoi.id,
                    TimeseriesStats.data_type == "lst",
                    TimeseriesStats.date >= thirty_days_ago,
                )
                .all()
            )

            if not baseline_stats or len(baseline_stats) < 3:
                return

            # Calculate 90th percentile
            values = sorted([s.mean_value for s in baseline_stats if s.mean_value])
            percentile_90 = values[int(len(values) * 0.9)]

            # Detect heat wave (> 90th percentile)
            if current_temp > percentile_90:
                severity = "critical" if current_temp > percentile_90 * 1.15 else "high"
                alert = Alert(
                    aoi_id=aoi.id,
                    alert_type="heat_wave",
                    severity=severity,
                    description=f"Heat wave conditions detected: {current_temp:.1f}°C (90th percentile: {percentile_90:.1f}°C)",
                    detected_at=datetime.utcnow(),
                    satellite_source="modis",
                    confidence_score=0.85,
                    geom=aoi.geom,
                )
                database.add(alert)
                database.commit()
                logger.info(f"Heat wave alert created for AOI {aoi.id}")

        except Exception as e:
            logger.error(f"Failed to detect heat wave anomalies: {e}")

    def get_heat_timeseries(
        self,
        aoi_id: int,
        database: Session,
        start_date: str,
        end_date: str,
    ) -> List[TimeseriesStats]:
        """
        Get LST time-series data.

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
                TimeseriesStats.data_type == "lst",
                TimeseriesStats.date >= start_date,
                TimeseriesStats.date <= end_date,
            )
            .order_by(TimeseriesStats.date)
            .all()
        )
