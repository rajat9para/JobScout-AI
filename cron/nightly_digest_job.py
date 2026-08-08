"""Nightly PDF digest job — runs every night at 10 PM IST on Render Cron.

Pipeline:
  1. Fetch user profile
  2. Query daily_digest table for today's un-sent matched jobs
  3. Join with jobs table for full details
  4. Generate professional PDF with all job descriptions
  5. Email the PDF as attachment via Brevo
  6. Mark digest entries as sent

This is the core of the new email-based alert system, replacing
the old Twilio WhatsApp instant alerts.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("jobscout.digest")


def run_nightly_digest():
    """Main entry point for the nightly PDF digest email."""
    logger.info("=" * 60)
    logger.info("🌙 Nightly digest job started")
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
        logger.error("❌ No profile found. Visit /setup to create one. Aborting.")
        return

    if profile.status != "active":
        logger.info(f"⏸️ Profile status: {profile.status}. Skipping digest.")
        return

    user_email = profile.email or settings.user_email
    logger.info(f"📧 Preparing digest for: {user_email}")

    # ── Step 2: Fetch pending digest jobs ──
    jobs = db.get_pending_digest_jobs(today)
    pending_count = len(jobs)
    logger.info(f"📋 Found {pending_count} jobs in today's digest queue")

    # ── Step 3: Generate PDF ──
    # We ALWAYS send a digest email (even if empty — so user knows the system is working)
    try:
        pdf_bytes = pdf_gen.generate(jobs, digest_date=today)
        pdf_size_kb = len(pdf_bytes) / 1024
        logger.info(f"📄 PDF generated: {pdf_size_kb:.1f} KB, {pending_count} jobs")
    except Exception as e:
        logger.error(f"❌ PDF generation failed: {e}")
        # Fallback: send email without PDF
        _send_error_notification(mailer, user_email, str(e))
        return

    # ── Step 4: Send email via Brevo ──
    try:
        success = mailer.send_digest_email(
            to_email=user_email,
            pdf_bytes=pdf_bytes,
            job_count=pending_count,
            digest_date=today,
        )
    except Exception as e:
        logger.error(f"❌ Email sending failed: {e}")
        success = False

    # ── Step 5: Mark as sent ──
    if success:
        db.mark_digest_sent(today)
        logger.info(f"✅ Digest sent to {user_email} with {pending_count} jobs")
    else:
        logger.error(f"❌ Digest email failed for {user_email}. "
                      "Jobs remain in queue for retry.")

    logger.info("=" * 60)
    logger.info(f"🌙 Nightly digest job finished. Sent: {success}, Jobs: {pending_count}")
    logger.info("=" * 60)


def _send_error_notification(mailer: BrevoMailer, to_email: str, error_msg: str):
    """Send a simple error notification if PDF generation fails."""
    try:
        import sib_api_v3_sdk
        from app.config import get_settings
        settings = get_settings()

        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": settings.sender_name, "email": settings.sender_email},
            subject="⚠️ JobScout Digest — Error",
            html_content=f"""
            <html><body style="font-family: sans-serif; padding: 20px;">
                <h2 style="color: #c5221f;">⚠️ Digest Generation Error</h2>
                <p>The nightly digest PDF could not be generated.</p>
                <p style="color: #666;">Error: {error_msg}</p>
                <p>The system will retry on the next cycle. Your jobs are safe in the queue.</p>
                <p style="font-size: 11px; color: #999;">— JobScout Bot</p>
            </body></html>
            """,
        )
        mailer._send_with_retry(email, "error-notification")
    except Exception as e:
        logger.error(f"Even error notification failed: {e}")


if __name__ == "__main__":
    run_nightly_digest()
