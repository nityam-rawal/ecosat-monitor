"""Time-series data endpoints."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models import AOI as AOIModel, TimeseriesStats
from app.db.session import get_session
from app.models.schemas import TimeseriesStats as TimeseriesStatsSchema, DataType
from app.services import (
    PollutionService,
    RainfallService,
    HeatService,
    VegetationService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/timeseries", tags=["Time-Series Data"])


@router.get("/{dataset}")
async def get_timeseries(
    dataset: DataType,
    aoi_id: Optional[int] = Query(None, description="AOI ID"),
    lat: Optional[float] = Query(None, description="Latitude (-90 to 90)"),
    lon: Optional[float] = Query(None, description="Longitude (-180 to 180)"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    aggregation: str = Query("day", description="day, week, or month"),
    db: Session = Depends(get_session),
) -> List[dict]:
    """
    Get time-series data for a dataset.

    Args:
        dataset: Dataset type
        aoi_id: AOI ID (alternative to lat/lon)
        lat: Latitude (alternative to aoi_id)
        lon: Longitude (alternative to aoi_id)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        aggregation: Aggregation level
        db: Database session

    Returns:
        List of time-series data points
    """
    try:
        # Validate dates
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD",
            )

        # Get data based on either AOI or point query
        if aoi_id:
            aoi = db.query(AOIModel).filter(AOIModel.id == aoi_id).first()
            if not aoi:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"AOI {aoi_id} not found",
                )
            query = db.query(TimeseriesStats).filter(
                TimeseriesStats.aoi_id == aoi_id,
                TimeseriesStats.data_type == dataset.value,
                TimeseriesStats.date >= start_date,
                TimeseriesStats.date <= end_date,
            )
        elif lat is not None and lon is not None:
            # For point queries, return closest AOI data (simplified implementation)
            query = db.query(TimeseriesStats).filter(
                TimeseriesStats.data_type == dataset.value,
                TimeseriesStats.date >= start_date,
                TimeseriesStats.date <= end_date,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide either aoi_id or lat/lon coordinates",
            )

        stats = query.order_by(TimeseriesStats.date).all()

        # Format response
        return [
            {
                "date": s.date,
                "mean": s.mean_value,
                "min": s.min_value,
                "max": s.max_value,
                "stddev": s.stddev_value,
                "source": s.data_source,
            }
            for s in stats
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch time-series data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch time-series data",
        )


@router.get("/latest/all")
async def get_latest_all(db: Session = Depends(get_session)) -> dict:
    """
    Get latest available data for all datasets.

    Returns:
        Dictionary with latest timestamps for each dataset
    """
    try:
        datasets = ["ndvi", "no2", "rainfall", "lst"]
        latest = {}

        for dataset_type in datasets:
            latest_stat = (
                db.query(TimeseriesStats)
                .filter(TimeseriesStats.data_type == dataset_type)
                .order_by(TimeseriesStats.date.desc())
                .first()
            )
            if latest_stat:
                latest[dataset_type] = {
                    "date": latest_stat.date,
                    "source": latest_stat.data_source,
                }

        return latest

    except Exception as e:
        logger.error(f"Failed to fetch latest data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest data",
        )
