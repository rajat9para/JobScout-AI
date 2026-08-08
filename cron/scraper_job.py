"""Scheduled scraper job — runs every hour on Render Cron.

Pipeline: Scrape → Extract (Gemini) → Deduplicate → Match → Queue to Daily Digest
Isolated per-source: one failure does not block others.

Jobs that match the user's profile are queued into the `daily_digest` table.
The nightly cron job (nightly_digest_job.py) picks them up, generates a PDF,
and emails it via Brevo.
"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.database import Database
from app.scraper import get_all_scrapers
from app.extractor import JobExtractor
from app.matcher import JobMatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("jobscout.cron")


def run_scraper_job():
    """Main entry point for the scheduled scraper."""
    logger.info("=" * 60)
    logger.info("🚀 JobScout scraper job started")
    logger.info("=" * 60)

    settings = get_settings()
    db = Database()
    extractor = JobExtractor()
    matcher = JobMatcher()

    # Get user profile (single-user mode)
    profile = db.get_profile_by_email(settings.user_email)
    if not profile:
        profile = db.get_first_active_profile()

    if not profile:
        logger.error("❌ No active profile found. Visit /setup to create one. Aborting.")
        return

    if profile.status != "active":
        logger.info(f"⏸️ Profile status: {profile.status}. Skipping.")
        return

    logger.info(f"👤 Profile: {profile.email} | {profile.qualification} | {profile.interests}")

    scrapers = get_all_scrapers()
    total_new = 0
    total_matches = 0
    total_queued = 0

    for scraper in scrapers:
        source = scraper.source_name
        logger.info(f"[{source}] Starting scrape...")

        try:
            raw_chunks = scraper.scrape()
            logger.info(f"[{source}] Scraped {len(raw_chunks)} chunks")

            source_new = 0
            source_matches = 0

            for chunk in raw_chunks:
                try:
                    jobs = extractor.extract(chunk, source)

                    for job in jobs:
                        # Deduplication
                        if db.job_exists(job.raw_hash):
                            continue

                        job_id = db.save_job(job)
                        if not job_id:
                            continue

                        source_new += 1
                        total_new += 1

                        # Matching
                        is_match = matcher.match(profile, job)

                        if is_match:
                            # Queue matched job for nightly PDF digest
                            queued = db.add_to_digest(job_id)
                            if queued:
                                total_queued += 1
                                logger.info(f"📋 Queued for digest: {job.title} @ {job.organization}")

                            source_matches += 1
                            total_matches += 1

                except Exception as e:
                    logger.error(f"[{source}] Chunk error: {e}")
                    continue

            logger.info(f"[{source}] Done. New: {source_new}, Matches: {source_matches}")

        except Exception as e:
            logger.error(f"[{source}] Scraper failed: {e}")
            continue

    logger.info("=" * 60)
    logger.info(f"✅ Done. New: {total_new}, Matches: {total_matches}, Queued: {total_queued}")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_scraper_job()
