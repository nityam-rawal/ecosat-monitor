"""AOI (Area of Interest) management endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from geoalchemy2.shape import to_shape
from shapely.geometry import shape
from shapely.geometry import mapping

from app.db.models import AOI as AOIModel
from app.db.session import get_session
from app.models.schemas import AOI, AOICreate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aois", tags=["AOI Management"])


def serialize_aoi(aoi: AOIModel) -> dict:
    """Convert an AOI database row into an API-friendly dict."""
    return {
        "id": aoi.id,
        "name": aoi.name,
        "geom": mapping(to_shape(aoi.geom)),
        "created_at": aoi.created_at,
    }


@router.post("", response_model=AOI, status_code=status.HTTP_201_CREATED)
async def create_aoi(aoi_data: AOICreate, db: Session = Depends(get_session)) -> AOI:
    """
    Create a new Area of Interest.

    Args:
        aoi_data: AOI creation data with GeoJSON geometry
        db: Database session

    Returns:
        Created AOI object
    """
    try:
        # Convert GeoJSON to shapely geometry
        geom_shape = shape(aoi_data.geom)
        aoi = AOIModel(
            name=aoi_data.name,
            geom=from_shape(geom_shape, srid=4326),
        )
        db.add(aoi)
        db.commit()
        db.refresh(aoi)
        logger.info(f"Created AOI: {aoi.id} - {aoi.name}")
        return serialize_aoi(aoi)
    except Exception as e:
        logger.error(f"Failed to create AOI: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create AOI: {str(e)}",
        )


@router.get("", response_model=List[AOI])
async def list_aois(db: Session = Depends(get_session)) -> List[AOI]:
    """
    List all Areas of Interest.

    Returns:
        List of AOI objects
    """
    aois = db.query(AOIModel).all()
    return [serialize_aoi(aoi) for aoi in aois]


@router.get("/{aoi_id}", response_model=AOI)
async def get_aoi(aoi_id: int, db: Session = Depends(get_session)) -> AOI:
    """
    Get a specific Area of Interest.

    Args:
        aoi_id: AOI ID
        db: Database session

    Returns:
        AOI object

    Raises:
        HTTPException: If AOI not found
    """
    aoi = db.query(AOIModel).filter(AOIModel.id == aoi_id).first()
    if not aoi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AOI {aoi_id} not found",
        )
    return serialize_aoi(aoi)


@router.delete("/{aoi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aoi(aoi_id: int, db: Session = Depends(get_session)) -> None:
    """
    Delete an Area of Interest.

    Args:
        aoi_id: AOI ID
        db: Database session

    Raises:
        HTTPException: If AOI not found
    """
    aoi = db.query(AOIModel).filter(AOIModel.id == aoi_id).first()
    if not aoi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AOI {aoi_id} not found",
        )
    db.delete(aoi)
    db.commit()
    logger.info(f"Deleted AOI: {aoi_id}")
