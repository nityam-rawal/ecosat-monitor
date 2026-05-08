"""Pydantic models and schemas for EcoSat Monitor API."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping


class DataType(str, Enum):
    """Available data types."""

    NDVI = "ndvi"
    NO2 = "no2"
    SO2 = "so2"
    CO = "co"
    O3 = "o3"
    CH4 = "ch4"
    RAINFALL = "rainfall"
    LST = "lst"


class AlertType(str, Enum):
    """Available alert types."""

    HEAT_WAVE = "heat_wave"
    DEFORESTATION = "deforestation"
    POLLUTION_SPIKE = "pollution_spike"
    FLOOD_RISK = "flood_risk"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataSource(str, Enum):
    """Data source identifiers."""

    SENTINEL2 = "sentinel-2"
    SENTINEL5P = "sentinel-5p"
    LANDSAT = "landsat"
    MODIS = "modis"
    GPM = "gpm"
    ERA5 = "era5"


class GeoJSONPoint(BaseModel):
    """GeoJSON point."""

    type: str = "Point"
    coordinates: List[float] = Field(..., description="[longitude, latitude]")


class GeoJSONPolygon(BaseModel):
    """GeoJSON polygon."""

    type: str = "Polygon"
    coordinates: List[List[List[float]]] = Field(
        ..., description="[[[lng, lat], [lng, lat], ...]]"
    )


class AOIBase(BaseModel):
    """Base AOI schema."""

    name: str = Field(..., min_length=1, max_length=255)
    geom: dict = Field(
        ..., description="GeoJSON geometry (Polygon or MultiPolygon) in EPSG:4326"
    )

    @validator("geom")
    def validate_geometry(cls, v):
        """Validate GeoJSON geometry."""
        if not isinstance(v, dict):
            raise ValueError("Geometry must be a GeoJSON object")
        geom_type = v.get("type")
        if geom_type not in ["Polygon", "MultiPolygon"]:
            raise ValueError("Geometry must be Polygon or MultiPolygon")
        return v


class AOICreate(AOIBase):
    """Schema for creating AOI."""

    pass


class AOI(AOIBase):
    """Schema for AOI response."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TimeseriesStatsBase(BaseModel):
    """Base timeseries stats schema."""

    aoi_id: int
    data_type: DataType
    date: str = Field(..., description="YYYY-MM-DD format")
    mean_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    stddev_value: Optional[float]
    data_source: DataSource


class TimeseriesStatsCreate(TimeseriesStatsBase):
    """Schema for creating timeseries stats."""

    pass


class TimeseriesStats(TimeseriesStatsBase):
    """Schema for timeseries stats response."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    """Base alert schema."""

    aoi_id: int
    alert_type: AlertType
    severity: AlertSeverity
    description: Optional[str] = None
    satellite_source: DataSource
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class AlertCreate(AlertBase):
    """Schema for creating alert."""

    geom: dict = Field(..., description="GeoJSON Point")


class Alert(AlertBase):
    """Schema for alert response."""

    id: int
    detected_at: datetime
    geom: dict

    class Config:
        from_attributes = True


class IngestionLogBase(BaseModel):
    """Base ingestion log schema."""

    data_type: DataType
    source: DataSource
    date_range: dict = Field(..., description="{'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}")
    status: str = Field(
        ..., description="pending, processing, completed, or failed"
    )
    records_processed: Optional[int] = None
    error_message: Optional[str] = None


class IngestionLogCreate(IngestionLogBase):
    """Schema for creating ingestion log."""

    pass


class IngestionLog(IngestionLogBase):
    """Schema for ingestion log response."""

    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TimeseriesQuery(BaseModel):
    """Query parameters for timeseries endpoint."""

    aoi_id: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    dataset: DataType
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    aggregation: str = Field(
        default="day", description="day, week, or month"
    )

    @validator("aggregation")
    def validate_aggregation(cls, v):
        """Validate aggregation parameter."""
        if v not in ["day", "week", "month"]:
            raise ValueError("Aggregation must be day, week, or month")
        return v


class DatasetMetadata(BaseModel):
    """Metadata for a dataset."""

    name: str
    data_type: DataType
    source: DataSource
    description: str
    temporal_resolution: str
    spatial_resolution: str
    unit: str
    last_update: Optional[datetime]
    color_scheme: dict


class HealthCheck(BaseModel):
    """Health check response."""

    status: str
    version: str
    database: str
    cache: str
