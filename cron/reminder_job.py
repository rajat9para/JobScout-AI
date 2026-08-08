"""Exam deadline reminder job.

Runs daily to check for jobs whose last_date is 3 days, 1 day, or today away.
Sends reminder emails via Brevo so users don't miss deadlines.
"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from app.config import get_settings
from app.database import Database
from app.brevo_mailer import BrevoMailer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("jobscout.reminders")


def run_reminder_job():
    """Check deadlines and send reminder emails."""
    logger.info("🔔 Reminder job started")

    settings = get_settings()
    db = Database()
    mailer = BrevoMailer()

    # Get user profile
    profile = db.get_profile_by_email(settings.user_email)
    if not profile:
        profile = db.get_first_active_profile()

    if not profile or profile.status != "active":
        logger.info("Profile inactive or not found. Skipping reminders.")
        return

    user_email = profile.email or settings.user_email

    # Check 3-day, 1-day, and same-day reminders
    reminder_days = [
        (3, "3_days"),
        (1, "1_day"),
        (0, "today"),
    ]

    total_sent = 0

    for days_offset, reminder_type in reminder_days:
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

                last_date_str = job.last_date.strftime("%d %b %Y") if job.last_date else "N/A"
                exam = job.exam_required or "Application"
                apply_link = job.apply_link or ""

                success = mailer.send_reminder_email(
                    to_email=user_email,
                    job_title=job.title,
                    organization=job.organization,
                    exam=exam,
                    last_date_str=last_date_str,
                    apply_link=apply_link,
                    days_left=days_offset,
                    reminder_type=reminder_type,
                )

                if success:
                    db.record_reminder(job.id, reminder_type)
                    total_sent += 1
                    logger.info(f"📧 Sent {reminder_type} reminder: {job.title}")
                else:
                    logger.error(f"❌ Failed to send {reminder_type} reminder: {job.title}")

        except Exception as e:
            logger.error(f"Reminder error for {reminder_type}: {e}")

    logger.info(f"🔔 Reminder job done. Sent: {total_sent}")


if __name__ == "__main__":
    run_reminder_job()
