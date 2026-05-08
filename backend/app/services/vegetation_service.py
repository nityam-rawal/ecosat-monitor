"""Vegetation data service module."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

import ee
from sqlalchemy.orm import Session

from app.core import GEEClient, DataIngestionException
from app.db.models import TimeseriesStats, Alert

logger = logging.getLogger(__name__)


class VegetationService:
    """Service for handling vegetation and NDVI data."""

    def __init__(self):
        """Initialize vegetation service."""
        self.gee_client = GEEClient()

    def ingest_vegetation_data(
        self,
        aoi: "AOI",  # type: ignore
        database: Session,
        start_date: str,
        end_date: str,
    ) -> Dict:
        """
        Ingest NDVI (vegetation) data for AOI.

        Args:
            aoi: Area of Interest object
            database: Database session
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with ingestion results
        """
        try:
            logger.info(f"Starting vegetation data ingestion for AOI {aoi.id}")

            # Convert geometry to ee.Geometry
            from shapely.geometry import shape

            geom_dict = shape(aoi.geom)
            ee_geometry = ee.Geometry.Polygon(
                [list(coords) for coords in geom_dict.exterior.coords]
            )

            # Get NDVI image from GEE (using 7-day median to reduce clouds)
            ndvi_image = self.gee_client.get_ndvi(
                ee_geometry, start_date, end_date, reducer="median"
            )

            if ndvi_image is None:
                raise DataIngestionException("No NDVI data available for date range")

            # Calculate statistics
            stats = self.gee_client.get_region_statistics(ndvi_image, ee_geometry)

            # Store in database
            ts_stat = TimeseriesStats(
                aoi_id=aoi.id,
                data_type="ndvi",
                date=end_date,
                mean_value=float(stats.get("mean", {}).get("NDVI", 0)),
                min_value=float(stats.get("min", {}).get("NDVI", 0)),
                max_value=float(stats.get("max", {}).get("NDVI", 0)),
                stddev_value=float(stats.get("stdDev", {}).get("NDVI", 0)),
                data_source="sentinel-2",
            )
            database.add(ts_stat)

            # Detect anomalies (vegetation loss/deforestation)
            self._detect_vegetation_anomalies(aoi, database, ts_stat.mean_value)

            database.commit()

            logger.info(f"Successfully ingested vegetation data for AOI {aoi.id}")
            return {
                "status": "success",
                "aoi_id": aoi.id,
                "data_type": "ndvi",
                "mean_value": ts_stat.mean_value,
            }

        except Exception as e:
            logger.error(f"Failed to ingest vegetation data: {e}")
            raise DataIngestionException(f"Vegetation data ingestion failed: {e}")

    def _detect_vegetation_anomalies(
        self,
        aoi: "AOI",  # type: ignore
        database: Session,
        current_ndvi: float,
    ) -> None:
        """
        Detect vegetation anomalies (deforestation, stress).

        Args:
            aoi: Area of Interest
            database: Database session
            current_ndvi: Current NDVI value
        """
        try:
            # Get year-over-year comparison (same period last year)
            one_year_ago = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")
            current_date = datetime.utcnow().strftime("%Y-%m-%d")

            # Get historical baseline (same 7-day period from last year)
            last_year_stats = (
                database.query(TimeseriesStats)
                .filter(
                    TimeseriesStats.aoi_id == aoi.id,
                    TimeseriesStats.data_type == "ndvi",
                    TimeseriesStats.date >= one_year_ago,
                )
                .all()
            )

            if not last_year_stats:
                return

            # Calculate baseline NDVI
            baseline_values = [s.mean_value for s in last_year_stats if s.mean_value]
            if not baseline_values:
                return

            baseline_ndvi = sum(baseline_values) / len(baseline_values)

            # Detect significant decrease (> 0.2 NDVI drop)
            if current_ndvi < baseline_ndvi - 0.2:
                severity = "critical" if current_ndvi < baseline_ndvi - 0.35 else "high"
                alert = Alert(
                    aoi_id=aoi.id,
                    alert_type="deforestation",
                    severity=severity,
                    description=f"Vegetation loss detected: NDVI {current_ndvi:.3f} (baseline: {baseline_ndvi:.3f})",
                    detected_at=datetime.utcnow(),
                    satellite_source="sentinel-2",
                    confidence_score=0.80,
                    geom=aoi.geom,
                )
                database.add(alert)
                database.commit()
                logger.info(f"Deforestation alert created for AOI {aoi.id}")

        except Exception as e:
            logger.error(f"Failed to detect vegetation anomalies: {e}")

    def get_vegetation_timeseries(
        self,
        aoi_id: int,
        database: Session,
        start_date: str,
        end_date: str,
    ) -> List[TimeseriesStats]:
        """
        Get NDVI time-series data.

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
                TimeseriesStats.data_type == "ndvi",
                TimeseriesStats.date >= start_date,
                TimeseriesStats.date <= end_date,
            )
            .order_by(TimeseriesStats.date)
            .all()
        )
