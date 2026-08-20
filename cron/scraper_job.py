"""Scheduled scraper job — runs every hour on Render Cron.

Pipeline: Scrape → Extract (Gemini) → Deduplicate → Match → Queue to Daily Digest
Isolated per-source: one failure does not block others.

Jobs that match the user's profile are queued into the `daily_digest` table.
The digest job picks them up, generates a PDF, and emails it via Brevo.

Safety net: if ZERO matches after a full scrape but new jobs were found,
queue all new jobs anyway — better to send too many than zero.
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
    total_skipped_dedup = 0
    total_extraction_failures = 0
    all_new_job_ids = []  # Track all new jobs for safety net

    for scraper in scrapers:
        source = scraper.source_name
        logger.info(f"─── [{source}] Starting scrape... ───")

        try:
            raw_chunks = scraper.scrape()
            logger.info(f"[{source}] Scraped {len(raw_chunks)} chunks")

            if not raw_chunks:
                logger.warning(f"[{source}] ⚠️ No data scraped — site may be blocking or down")
                continue

            source_new = 0
            source_matches = 0
            source_dedup = 0

            for chunk_idx, chunk in enumerate(raw_chunks):
                try:
                    jobs = extractor.extract(chunk, source)

                    if not jobs:
                        logger.info(f"[{source}] Chunk {chunk_idx + 1}: no jobs extracted "
                                    f"(text: {len(chunk)} chars)")
                        total_extraction_failures += 1
                        continue

                    logger.info(f"[{source}] Chunk {chunk_idx + 1}: extracted {len(jobs)} jobs")

                    for job in jobs:
                        # Deduplication
                        if db.job_exists(job.raw_hash):
                            source_dedup += 1
                            total_skipped_dedup += 1
                            continue

                        job_id = db.save_job(job)
                        if not job_id:
                            continue

                        source_new += 1
                        total_new += 1
                        all_new_job_ids.append(job_id)

                        # Matching
                        is_match = matcher.match(profile, job)

                        if is_match:
                            # Queue matched job for PDF digest
                            queued = db.add_to_digest(job_id)
                            if queued:
                                total_queued += 1
                                logger.info(f"📋 Queued for digest: {job.title} @ {job.organization}")

                            source_matches += 1
                            total_matches += 1

                except Exception as e:
                    logger.error(f"[{source}] Chunk {chunk_idx + 1} error: {e}")
                    continue

            logger.info(f"[{source}] Done. New: {source_new}, Matches: {source_matches}, "
                        f"Dedup skipped: {source_dedup}")

        except Exception as e:
            logger.error(f"[{source}] Scraper failed: {e}")
            continue

    # ── Safety net: if we found new jobs but zero matches, queue them all ──
    if total_new > 0 and total_matches == 0:
        logger.warning(f"⚠️ SAFETY NET: {total_new} new jobs found but 0 matched profile. "
                       f"Queuing ALL new jobs to ensure digest has content.")
        safety_queued = 0
        for job_id in all_new_job_ids:
            if db.add_to_digest(job_id):
                safety_queued += 1
        total_queued = safety_queued
        logger.info(f"📋 Safety net queued {safety_queued} jobs for digest")

    logger.info("=" * 60)
    logger.info(f"✅ Scraper complete:")
    logger.info(f"   📥 New jobs saved:     {total_new}")
    logger.info(f"   ✅ Profile matches:    {total_matches}")
    logger.info(f"   📋 Queued for digest:  {total_queued}")
    logger.info(f"   🔄 Dedup skipped:      {total_skipped_dedup}")
    logger.info(f"   ⚠️ Extract failures:   {total_extraction_failures}")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_scraper_job()
