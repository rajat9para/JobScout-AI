"""Built-in job scheduler — runs all cron jobs inside the web service.

No separate Render cron services needed. This uses APScheduler to run:
  - Scraper:          Every hour at :05
  - Morning Digest:   10:00 AM IST daily (4:30 AM UTC)
  - Evening Digest:    6:00 PM IST daily (12:30 PM UTC)
  - Deadline Reminders: 8:00 AM IST daily (2:30 AM UTC)
  - DB Keep-Alive:    Every 8 hours (prevents Supabase free-tier sleep)

All jobs run in background threads so the FastAPI server stays responsive.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz

logger = logging.getLogger("jobscout.scheduler")

# IST timezone
IST = pytz.timezone("Asia/Kolkata")

scheduler = BackgroundScheduler(timezone=IST)


def _run_scraper():
    """Background: scrape all sources, extract, match, queue."""
    try:
        from cron.scraper_job import run_scraper_job
        run_scraper_job()
    except Exception as e:
        logger.error(f"Scheduled scraper failed: {e}")


def _run_morning_digest():
    """Background: generate and send morning PDF digest."""
    try:
        from cron.nightly_digest_job import run_digest
        run_digest("morning")
    except Exception as e:
        logger.error(f"Morning digest failed: {e}")


def _run_evening_digest():
    """Background: generate and send evening PDF digest."""
    try:
        from cron.nightly_digest_job import run_digest
        run_digest("evening")
    except Exception as e:
        logger.error(f"Evening digest failed: {e}")


def _run_reminders():
    """Background: send deadline reminder emails."""
    try:
        from cron.reminder_job import run_reminder_job
        run_reminder_job()
    except Exception as e:
        logger.error(f"Reminder job failed: {e}")


def _run_db_keepalive():
    """Ping Supabase database to prevent free-tier sleep.

    Supabase pauses inactive databases after 7 days on the free plan.
    This runs every 8 hours (3 times/day) to keep the database alive
    by executing a lightweight SELECT query on the profiles table.
    """
    try:
        from app.database import Database
        db = Database()

        # Lightweight query — just count profiles
        result = db.client.table("profiles").select("id", count="exact").limit(1).execute()
        count = result.count if result.count is not None else 0

        # Also touch digest_history to keep it warm
        db.client.table("digest_history").select("id", count="exact").limit(1).execute()

        # And touch jobs table
        db.client.table("jobs").select("id", count="exact").limit(1).execute()

        logger.info(f"💓 DB keep-alive OK — {count} profile(s), all tables responsive")
    except Exception as e:
        logger.error(f"💔 DB keep-alive FAILED: {e}")


def start_scheduler():
    """Start all scheduled jobs. Call once during app startup."""
    if scheduler.running:
        logger.info("Scheduler already running, skipping start")
        return

    # ── Scraper: every hour at :05 ──
    scheduler.add_job(
        _run_scraper,
        CronTrigger(minute=5, timezone=IST),
        id="scraper",
        name="Hourly Job Scraper",
        replace_existing=True,
        misfire_grace_time=300,
    )

    # ── Morning Digest: 10:00 AM IST ──
    scheduler.add_job(
        _run_morning_digest,
        CronTrigger(hour=10, minute=0, timezone=IST),
        id="morning_digest",
        name="Morning PDF Digest (10 AM IST)",
        replace_existing=True,
        misfire_grace_time=600,
    )

    # ── Evening Digest: 6:00 PM IST ──
    scheduler.add_job(
        _run_evening_digest,
        CronTrigger(hour=18, minute=0, timezone=IST),
        id="evening_digest",
        name="Evening PDF Digest (6 PM IST)",
        replace_existing=True,
        misfire_grace_time=600,
    )

    # ── Deadline Reminders: 8:00 AM IST ──
    scheduler.add_job(
        _run_reminders,
        CronTrigger(hour=8, minute=0, timezone=IST),
        id="reminders",
        name="Deadline Reminders (8 AM IST)",
        replace_existing=True,
        misfire_grace_time=600,
    )

    # ── DB Keep-Alive: Every 8 hours (3x daily) ──
    scheduler.add_job(
        _run_db_keepalive,
        IntervalTrigger(hours=8, timezone=IST),
        id="db_keepalive",
        name="Supabase Keep-Alive (Every 8h)",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.start()

    # Run keep-alive immediately on startup
    try:
        _run_db_keepalive()
    except Exception:
        pass

    logger.info("=" * 50)
    logger.info("📅 Scheduler started with 5 jobs:")
    logger.info("   🔍 Scraper        → Every hour at :05")
    logger.info("   🌅 Morning Digest → 10:00 AM IST")
    logger.info("   🌇 Evening Digest →  6:00 PM IST")
    logger.info("   🔔 Reminders      →  8:00 AM IST")
    logger.info("   💓 DB Keep-Alive  →  Every 8 hours")
    logger.info("=" * 50)


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("📅 Scheduler stopped")

