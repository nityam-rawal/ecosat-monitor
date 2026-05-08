"""SQLAlchemy models for EcoSat Monitor database."""

import logging
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Float, Integer, String, Index, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class AOI(Base):
    """Area of Interest model."""

    __tablename__ = "aois"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    timeseries_stats = relationship(
        "TimeseriesStats", back_populates="aoi", cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="aoi", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_aois_geom", geom, postgresql_using="gist"),)


class TimeseriesStats(Base):
    """Time-series statistics model."""

    __tablename__ = "timeseries_stats"

    id = Column(Integer, primary_key=True)
    aoi_id = Column(Integer, ForeignKey("aois.id"), nullable=False)
    data_type = Column(String(50), nullable=False)  # 'ndvi', 'no2', 'rainfall', 'lst'
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    mean_value = Column(Float)
    min_value = Column(Float)
    max_value = Column(Float)
    stddev_value = Column(Float)
    data_source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    aoi = relationship("AOI", back_populates="timeseries_stats")

    __table_args__ = (
        Index("idx_timeseries_lookup", "aoi_id", "data_type", "date"),
    )


class Alert(Base):
    """Alert/anomaly event model."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    aoi_id = Column(Integer, ForeignKey("aois.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # 'heat_wave', 'deforestation', etc.
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    description = Column(String(1000))
    detected_at = Column(DateTime, default=datetime.utcnow)
    satellite_source = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    aoi = relationship("AOI", back_populates="alerts")

    __table_args__ = (Index("idx_alerts_geom", geom, postgresql_using="gist"),)


class IngestionLog(Base):
    """Data ingestion process log model."""

    __tablename__ = "ingestion_logs"

    id = Column(Integer, primary_key=True)
    data_type = Column(String(50), nullable=False)
    source = Column(String(100), nullable=False)
    date_range_start = Column(String(10), nullable=False)  # YYYY-MM-DD
    date_range_end = Column(String(10), nullable=False)  # YYYY-MM-DD
    status = Column(String(20), nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    records_processed = Column(Integer)
    error_message = Column(String(1000))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
