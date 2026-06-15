from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from app.core.config import settings

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
    return _scheduler


def _setup_jobs(scheduler: AsyncIOScheduler):
    pass


def start_scheduler():
    scheduler = get_scheduler()

    if scheduler.running:
        logger.warning("Scheduler is already running, skipping start")
        return

    if settings.ENVIRONMENT == "dev":
        logger.info("Development environment detected, scheduler skipped")
        return

    try:
        _setup_jobs(scheduler)
        scheduler.start()

        jobs = scheduler.get_jobs()
        if jobs:
            logger.info(f"Scheduler started with {len(jobs)} jobs")
            for job in jobs:
                logger.info(f"Task: {job.id} | Next: {job.next_run_time}")
        else:
            logger.info("Scheduler started with no jobs")

    except Exception as e:
        logger.error(f"Scheduler start failed: {e}")
        raise


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        try:
            _scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Scheduler stop failed: {e}")
