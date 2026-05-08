"""Database session and base configuration."""

import logging
from typing import Generator

from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
    poolclass=NullPool if settings.DEBUG else pool.QueuePool,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def get_session() -> Generator[Session, None, None]:
    """Get database session dependency."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Initialize database tables."""
    from app.db.models import Base

    logger.info("Creating database tables...")
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
