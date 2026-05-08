"""Dataset metadata endpoints."""

import logging
from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.schemas import DatasetMetadata, DataType, DataSource

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


# Dataset definitions
DATASETS = {
    "ndvi": DatasetMetadata(
        name="Vegetation Index (NDVI)",
        data_type=DataType.NDVI,
        source=DataSource.SENTINEL2,
        description="Normalized Difference Vegetation Index from Sentinel-2 satellite imagery",
        temporal_resolution="5-7 days",
        spatial_resolution="10 meters",
        unit="dimensionless (-1 to 1)",
        last_update=datetime.utcnow(),
        color_scheme={
            "0": "#ff0000",  # Red - unhealthy
            "0.3": "#ffff00",  # Yellow
            "0.6": "#00ff00",  # Green - healthy
        },
    ),
    "no2": DatasetMetadata(
        name="Nitrogen Dioxide (NO₂)",
        data_type=DataType.NO2,
        source=DataSource.SENTINEL5P,
        description="Atmospheric NO₂ concentration from Sentinel-5P TROPOMI",
        temporal_resolution="daily",
        spatial_resolution="~7km × 3.5km",
        unit="mol/m²",
        last_update=datetime.utcnow(),
        color_scheme={
            "0": "#0000ff",  # Blue - low
            "500": "#8000ff",  # Purple
            "1000": "#ff0000",  # Red - high
        },
    ),
    "so2": DatasetMetadata(
        name="Sulfur Dioxide (SO₂)",
        data_type=DataType.SO2,
        source=DataSource.SENTINEL5P,
        description="Atmospheric SO₂ concentration from Sentinel-5P TROPOMI",
        temporal_resolution="daily",
        spatial_resolution="~7km × 3.5km",
        unit="mol/m²",
        last_update=datetime.utcnow(),
        color_scheme={
            "0": "#0000ff",  # Blue - low
            "500": "#ff8000",  # Orange
            "1000": "#ff0000",  # Red - high
        },
    ),
    "co": DatasetMetadata(
        name="Carbon Monoxide (CO)",
        data_type=DataType.CO,
        source=DataSource.SENTINEL5P,
        description="Atmospheric CO concentration from Sentinel-5P TROPOMI",
        temporal_resolution="daily",
        spatial_resolution="~7km × 3.5km",
        unit="mol/m²",
        last_update=datetime.utcnow(),
        color_scheme={
            "0": "#00ff00",  # Green - low
            "5000": "#ffff00",  # Yellow
            "10000": "#ff0000",  # Red - high
        },
    ),
    "o3": DatasetMetadata(
        name="Ozone (O₃)",
        data_type=DataType.O3,
        source=DataSource.SENTINEL5P,
        description="Total ozone column from Sentinel-5P TROPOMI",
        temporal_resolution="daily",
        spatial_resolution="~7km × 3.5km",
        unit="mol/m²",
        last_update=datetime.utcnow(),
        color_scheme={
            "200": "#0000ff",  # Blue - low
            "400": "#ff8000",  # Orange
            "600": "#ff0000",  # Red - high
        },
    ),
    "ch4": DatasetMetadata(
        name="Methane (CH₄)",
        data_type=DataType.CH4,
        source=DataSource.SENTINEL5P,
        description="Atmospheric CH₄ concentration from Sentinel-5P TROPOMI",
        temporal_resolution="daily",
        spatial_resolution="~7km × 3.5km",
        unit="ppb",
        last_update=datetime.utcnow(),
        color_scheme={
            "1700": "#0000ff",  # Blue - low
            "1800": "#ffff00",  # Yellow
            "1900": "#ff0000",  # Red - high
        },
    ),
    "rainfall": DatasetMetadata(
        name="Rainfall / Precipitation",
        data_type=DataType.RAINFALL,
        source=DataSource.GPM,
        description="Precipitation estimates from NASA GPM IMERG",
        temporal_resolution="half-hourly (accumulated)",
        spatial_resolution="0.1° (~11km)",
        unit="mm",
        last_update=datetime.utcnow(),
        color_scheme={
            "0": "#ffffff",  # White - no rain
            "10": "#80ccff",  # Light blue
            "50": "#0080ff",  # Blue - moderate
            "100": "#0000ff",  # Dark blue - heavy
        },
    ),
    "lst": DatasetMetadata(
        name="Land Surface Temperature (LST)",
        data_type=DataType.LST,
        source=DataSource.MODIS,
        description="Daily land surface temperature from MODIS satellite",
        temporal_resolution="daily",
        spatial_resolution="1km",
        unit="°Celsius",
        last_update=datetime.utcnow(),
        color_scheme={
            "-20": "#0000ff",  # Blue - cold
            "0": "#00ffff",  # Cyan
            "20": "#00ff00",  # Green - moderate
            "40": "#ffff00",  # Yellow - warm
            "60": "#ff0000",  # Red - hot
        },
    ),
}


@router.get("", response_model=List[DatasetMetadata])
async def list_datasets(db: Session = Depends(get_session)) -> List[DatasetMetadata]:
    """
    List all available datasets with metadata.

    Returns:
        List of dataset metadata
    """
    return list(DATASETS.values())


@router.get("/{dataset_id}", response_model=DatasetMetadata)
async def get_dataset(dataset_id: str, db: Session = Depends(get_session)) -> DatasetMetadata:
    """
    Get metadata for a specific dataset.

    Args:
        dataset_id: Dataset identifier
        db: Database session

    Returns:
        Dataset metadata
    """
    dataset = DATASETS.get(dataset_id)
    if not dataset:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Dataset {dataset_id} not found",
        )
    return dataset
