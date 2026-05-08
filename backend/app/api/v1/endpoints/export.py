"""Data export endpoints."""

import csv
import io
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.models import AOI as AOIModel, TimeseriesStats
from app.db.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/geojson")
async def export_geojson(
    aoi_id: int = Query(..., description="AOI ID to export"),
    db: Session = Depends(get_session),
) -> dict:
    """
    Export AOI as GeoJSON.

    Args:
        aoi_id: AOI ID
        db: Database session

    Returns:
        GeoJSON FeatureCollection
    """
    try:
        aoi = db.query(AOIModel).filter(AOIModel.id == aoi_id).first()
        if not aoi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AOI {aoi_id} not found",
            )

        from geoalchemy2.shape import to_shape

        geom = to_shape(aoi.geom)
        feature = {
            "type": "Feature",
            "geometry": json.loads(json.dumps(geom.__geo_interface__)),
            "properties": {
                "id": aoi.id,
                "name": aoi.name,
                "created_at": aoi.created_at.isoformat(),
            },
        }

        return {
            "type": "FeatureCollection",
            "features": [feature],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export GeoJSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export GeoJSON",
        )


@router.get("/csv")
async def export_csv(
    aoi_id: int = Query(..., description="AOI ID"),
    dataset: str = Query(..., description="Dataset type"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_session),
) -> StreamingResponse:
    """
    Export time-series data as CSV.

    Args:
        aoi_id: AOI ID
        dataset: Dataset type
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        db: Database session

    Returns:
        CSV file as streaming response
    """
    try:
        # Get time-series data
        stats = (
            db.query(TimeseriesStats)
            .filter(
                TimeseriesStats.aoi_id == aoi_id,
                TimeseriesStats.data_type == dataset,
                TimeseriesStats.date >= start_date,
                TimeseriesStats.date <= end_date,
            )
            .order_by(TimeseriesStats.date)
            .all()
        )

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data found for specified criteria",
            )

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "mean", "min", "max", "stddev", "source"])

        for stat in stats:
            writer.writerow(
                [
                    stat.date,
                    stat.mean_value,
                    stat.min_value,
                    stat.max_value,
                    stat.stddev_value,
                    stat.data_source,
                ]
            )

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={dataset}_{start_date}_{end_date}.csv"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export CSV",
        )
