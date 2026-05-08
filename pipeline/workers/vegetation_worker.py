"""Celery worker for vegetation data ingestion."""

import logging
from datetime import datetime, timedelta

from celery import Celery

from app.config import get_settings
from app.db.session import SessionLocal
from app.services import VegetationService

settings = get_settings()
logger = logging.getLogger(__name__)

app = Celery(
    "vegetation_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


@app.task(name="ingest_vegetation", bind=True, max_retries=3)
def ingest_vegetation(self, aoi_id: int):
    """
    Celery task for vegetation (NDVI) data ingestion.

    Args:
        aoi_id: Area of Interest ID
    """
    db = SessionLocal()
    service = VegetationService()

    try:
        from app.db.models import AOI

        aoi = db.query(AOI).filter(AOI.id == aoi_id).first()
        if not aoi:
            logger.error(f"AOI {aoi_id} not found")
            return {"status": "error", "message": f"AOI {aoi_id} not found"}

        # Ingest data for last 7 days (to account for cloud cover)
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        result = service.ingest_vegetation_data(aoi, db, start_date, end_date)
        logger.info(f"Vegetation ingestion completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"Vegetation ingestion failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

    finally:
        db.close()


if __name__ == "__main__":
    app.start()
