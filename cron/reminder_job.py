"""Exam deadline reminder job.

Runs daily to check for jobs whose last_date is 3 days, 1 day, or today away.
Sends reminder WhatsApp messages so users don't miss deadlines.
"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from app.config import get_settings
from app.database import Database
from app.twilio_client import TwilioWhatsApp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("jobscout.reminders")


def run_reminder_job():
    """Check deadlines and send reminders."""
    logger.info("🔔 Reminder job started")

    settings = get_settings()
    db = Database()
    twilio = TwilioWhatsApp()

    profile = db.get_profile_by_whatsapp(settings.user_whatsapp_number)
    if not profile or profile.status != "active":
        logger.info("Profile inactive. Skipping reminders.")
        return

    # Check 3-day, 1-day, and same-day reminders
    reminder_days = [
        (3, "3_days", "⏰ *3 Days Left!*"),
        (1, "1_day", "⚠️ *1 Day Left!*"),
        (0, "today", "🔥 *Last Day Today!*"),
    ]

    total_sent = 0

    for days_offset, reminder_type, header in reminder_days:
        target_date = (date.today() + timedelta(days=days_offset)).isoformat()

        try:
            from app.models import Job
            result = db.client.table("jobs").select("*").eq("last_date", target_date).execute()
            jobs = [Job(**row) for row in result.data]

            for job in jobs:
                if db.reminder_exists(job.id, reminder_type):
                    continue

                # Only remind for matched jobs
                from app.matcher import JobMatcher
                matcher = JobMatcher()
                if not matcher.match(profile, job):
                    continue

                success = twilio.send_exam_reminder(profile.whatsapp_number, job)
                if success:
                    db.record_reminder(job.id, reminder_type)
                    total_sent += 1
                    logger.info(f"Sent {reminder_type} reminder: {job.title}")

        except Exception as e:
            logger.error(f"Reminder error for {reminder_type}: {e}")

    logger.info(f"🔔 Reminder job done. Sent: {total_sent}")


if __name__ == "__main__":
    run_reminder_job()
