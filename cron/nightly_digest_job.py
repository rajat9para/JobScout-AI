"""PDF digest job — runs twice daily.

Schedule:
  Morning:  10:00 AM IST  → run_digest("morning")
  Evening:   6:00 PM IST  → run_digest("evening")

Pipeline:
  1. Fetch user profile
  2. 3-tier job fetch strategy:
     a) Today's pending digest queue
     b) ALL unsent backlog entries from any date
     c) FALLBACK: Last 15 days of jobs from jobs table (profile-filtered)
  3. Group jobs by date (recent first)
  4. Generate professional PDF with date-grouped layout
  5. Email the PDF as attachment via Brevo
  6. Mark digest entries as sent
  7. Record in digest_history for dashboard tracking
"""
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from app.config import get_settings
from app.database import Database
from app.pdf_generator import PDFGenerator
from app.brevo_mailer import BrevoMailer
from app.matcher import JobMatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("jobscout.digest")


def run_digest(digest_type: str = "scheduled"):
    """Main entry point for the PDF digest email.

    Args:
        digest_type: "morning", "evening", "manual", or "scheduled"
    """
    label = {
        "morning": "🌅 Morning",
        "evening": "🌇 Evening",
        "manual": "⚡ Manual",
        "scheduled": "📧 Scheduled",
    }.get(digest_type, "📧")

    logger.info("=" * 60)
    logger.info(f"{label} digest job started")
    logger.info("=" * 60)

    settings = get_settings()
    db = Database()
    pdf_gen = PDFGenerator()
    mailer = BrevoMailer()

    today = date.today()

    # ── Step 1: Get user profile ──
    profile = db.get_profile_by_email(settings.user_email)
    if not profile:
        profile = db.get_first_active_profile()

    if not profile:
        logger.error("❌ No profile found. Visit the dashboard to create one.")
        return

    if profile.status != "active":
        logger.info(f"⏸️ Profile status: {profile.status}. Skipping digest.")
        return

    user_email = profile.email or settings.user_email
    logger.info(f"📧 Preparing {digest_type} digest for: {user_email}")

    # ── Step 2: 3-tier job fetch strategy ──
    jobs = []
    source = "empty"

    # Strategy 1: Today's pending digest queue
    jobs = db.get_pending_digest_jobs(today)
    source = "queued"
    logger.info(f"📋 Strategy 1 (today's queue): {len(jobs)} jobs")

    # Strategy 2: ALL unsent backlog entries from any date
    if not jobs:
        jobs = db.get_all_pending_digest_jobs()
        source = "backlog"
        logger.info(f"📋 Strategy 2 (unsent backlog): {len(jobs)} jobs")

    # Strategy 3: Last 15 days of jobs directly from DB
    if not jobs:
        logger.info("📋 Strategy 3: Fetching last 15 days of jobs...")
        all_recent = db.get_jobs_last_n_days(days=15)
        logger.info(f"📋 Found {len(all_recent)} total jobs in last 15 days")

        # Filter by profile match
        if all_recent:
            matcher = JobMatcher()
            jobs = [j for j in all_recent if matcher.match(profile, j)]
            logger.info(f"📋 After profile filter: {len(jobs)} matching jobs")

            # If still no matches, include ALL recent jobs
            if not jobs:
                jobs = all_recent
                logger.warning(f"⚠️ No profile matches — including all {len(jobs)} recent jobs")

        source = "15day_window"

    job_count = len(jobs)
    logger.info(f"📋 Final job count for digest: {job_count} (source: {source})")

    # Compute match scores for all included jobs
    matcher = JobMatcher()
    for j in jobs:
        if not j.match_score:
            j.match_score = matcher.compute_match_percentage(profile, j)

    # ── Step 3: Generate PDF ──
    try:
        pdf_bytes = pdf_gen.generate(jobs, digest_date=today)
        pdf_size_kb = len(pdf_bytes) / 1024
        logger.info(f"📄 PDF generated: {pdf_size_kb:.1f} KB, {job_count} jobs")
    except Exception as e:
        logger.error(f"❌ PDF generation failed: {e}")
        _send_error_notification(mailer, user_email, settings, str(e))
        return

    # ── Step 4: Send email via Brevo ──
    try:
        success = mailer.send_digest_email(
            to_email=user_email,
            pdf_bytes=pdf_bytes,
            job_count=job_count,
            digest_date=today,
        )
    except Exception as e:
        logger.error(f"❌ Email sending failed: {e}")
        success = False

    # ── Step 5: Mark as sent + record history ──
    if success:
        if source in ("queued", "backlog"):
            db.mark_digest_sent(today)
        db.record_digest_history(job_count, digest_type)
        logger.info(f"✅ {label} digest sent to {user_email} with {job_count} jobs (source: {source})")
    else:
        logger.error(f"❌ Digest email failed. Jobs remain in queue for next run.")

    logger.info("=" * 60)
    logger.info(f"{label} digest job finished. Sent: {success}, Jobs: {job_count}")
    logger.info("=" * 60)


def _send_error_notification(mailer, to_email, settings, error_msg):
    """Send a simple error notification if PDF generation fails."""
    try:
        import sib_api_v3_sdk
        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": settings.sender_name, "email": settings.sender_email},
            subject="⚠️ JobScout-AI — Digest Error",
            html_content=f"""
            <html><body style="font-family: sans-serif; padding: 20px;">
                <h2 style="color: #c5221f;">⚠️ Digest Generation Error</h2>
                <p>The digest PDF could not be generated.</p>
                <p style="color: #666;">Error: {error_msg}</p>
                <p>Your jobs are safe in the queue and will be included in the next digest.</p>
                <p style="font-size: 11px; color: #999;">— JobScout-AI</p>
            </body></html>
            """,
        )
        mailer._send_with_retry(email, "error-notification")
    except Exception as e:
        logger.error(f"Even error notification failed: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="JobScout-AI PDF Digest")
    parser.add_argument("--type", default="scheduled",
                        choices=["morning", "evening", "manual", "scheduled"],
                        help="Type of digest: morning, evening, manual, or scheduled")
    args = parser.parse_args()
    run_digest(args.type)
