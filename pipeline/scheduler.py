"""Scheduler for automated data ingestion tasks."""

import logging
from datetime import datetime, time

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings
from app.db.session import SessionLocal
from app.db.models import AOI

settings = get_settings()
logger = logging.getLogger(__name__)

app = Celery(
    "scheduler",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Configure periodic tasks
app.conf.beat_schedule = {
    "ingest-pollution-daily": {
        "task": "ingest_pollution",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM UTC
        "kwargs": {"pollutant": "NO2"},
    },
    "ingest-rainfall-daily": {
        "task": "ingest_rainfall",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM UTC
    },
    "ingest-heat-daily": {
        "task": "ingest_heat",
        "schedule": crontab(hour=4, minute=0),  # Daily at 4 AM UTC
    },
    "ingest-vegetation-weekly": {
        "task": "ingest_vegetation",
        "schedule": crontab(day_of_week=0, hour=5, minute=0),  # Weekly on Sunday at 5 AM UTC
    },
}


@app.task(name="schedule_all_aoi_ingestions")
def schedule_all_aoi_ingestions():
    """Schedule ingestion tasks for all AOIs."""
    db = SessionLocal()
    try:
        aois = db.query(AOI).all()
        logger.info(f"Scheduling ingestion for {len(aois)} AOIs")

        for aoi in aois:
            # Import tasks
            from pipeline.workers.pollution_worker import ingest_pollution
            from pipeline.workers.rainfall_worker import ingest_rainfall
            from pipeline.workers.heat_worker import ingest_heat
            from pipeline.workers.vegetation_worker import ingest_vegetation

            # Schedule tasks
            ingest_pollution.delay(aoi.id, "NO2")
            ingest_pollution.delay(aoi.id, "SO2")
            ingest_pollution.delay(aoi.id, "CO")
            ingest_pollution.delay(aoi.id, "O3")
            ingest_rainfall.delay(aoi.id)
            ingest_heat.delay(aoi.id)
            ingest_vegetation.delay(aoi.id)

        logger.info("All ingestion tasks scheduled")

    except Exception as e:
        logger.error(f"Failed to schedule ingestions: {e}")
    finally:
        db.close()


@app.task(name="cleanup_old_data")
def cleanup_old_data():
    """Clean up data older than retention period."""
    db = SessionLocal()
    try:
        from datetime import timedelta
        from sqlalchemy import delete
        from app.db.models import TimeseriesStats, IngestionLog

        # Keep last 90 days of data
        cutoff_date = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")

        # Delete old timeseries stats
        deleted_count = db.execute(
            delete(TimeseriesStats).where(TimeseriesStats.date < cutoff_date)
        ).rowcount

        logger.info(f"Deleted {deleted_count} old timeseries records")

        # Delete old ingestion logs (keep 30 days)
        cutoff_datetime = datetime.utcnow() - timedelta(days=30)
        deleted_logs = db.execute(
            delete(IngestionLog).where(IngestionLog.created_at < cutoff_datetime)
        ).rowcount

        logger.info(f"Deleted {deleted_logs} old ingestion logs")
        db.commit()

    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    app.start()
