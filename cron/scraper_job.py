"""Scheduled scraper job — runs every hour on Render Cron.

Pipeline: Scrape → Extract (Gemini) → Deduplicate → Match → Alert
Isolated per-source: one failure does not block others.
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
from app.twilio_client import TwilioWhatsApp

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
    twilio = TwilioWhatsApp()

    profile = db.get_profile_by_whatsapp(settings.user_whatsapp_number)
    if not profile:
        logger.error(f"❌ No profile for {settings.user_whatsapp_number}. Aborting.")
        return

    if profile.status != "active":
        logger.info(f"⏸️ Profile status: {profile.status}. Skipping.")
        return

    logger.info(f"👤 Profile: {profile.qualification} | {profile.interests} | Mode: {profile.alert_mode}")

    scrapers = get_all_scrapers()
    total_new = 0
    total_matches = 0
    total_alerts = 0
    matched_jobs = []  # For digest mode

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

                        # BULK mode: send everything
                        # INSTANT mode: send only matches
                        # DIGEST mode: collect matches for later
                        should_alert = False

                        if profile.alert_mode == "bulk":
                            should_alert = True
                        elif profile.alert_mode == "instant" and is_match:
                            should_alert = True
                        elif profile.alert_mode == "digest" and is_match:
                            matched_jobs.append(job)
                            should_alert = False

                        if should_alert:
                            if db.alert_exists(job_id):
                                continue

                            success = twilio.send_job_alert(profile.whatsapp_number, job)
                            if success:
                                db.record_alert(job_id)
                                total_alerts += 1
                                source_matches += 1
                            else:
                                logger.error(f"[{source}] Alert failed: {job.title}")

                        if is_match:
                            source_matches += 1
                            total_matches += 1

                except Exception as e:
                    logger.error(f"[{source}] Chunk error: {e}")
                    continue

            logger.info(f"[{source}] Done. New: {source_new}, Matches: {source_matches}")

        except Exception as e:
            logger.error(f"[{source}] Scraper failed: {e}")
            continue

    # Send digest if in digest mode and there are matched jobs
    if profile.alert_mode == "digest" and matched_jobs:
        success = twilio.send_digest(profile.whatsapp_number, matched_jobs)
        if success:
            for job in matched_jobs:
                # Record alerts for all digest jobs
                # We need job IDs which we didn't track — this is a simplification
            logger.info(f"📋 Digest sent with {len(matched_jobs)} jobs")

    logger.info("=" * 60)
    logger.info(f"✅ Done. New: {total_new}, Matches: {total_matches}, Alerts: {total_alerts}")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_scraper_job()
