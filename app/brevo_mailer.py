"""Brevo (Sendinblue) transactional email client.

Handles sending the nightly PDF digest and deadline reminder emails.
Uses the official sib-api-v3-sdk Python SDK.

Brevo Free Tier: 300 emails/day, 9000 emails/month — more than enough
for a single-user daily digest.
"""
import base64
import logging
import time
import re
from datetime import date
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.config import get_settings

logger = logging.getLogger(__name__)


class BrevoMailer:
    """Robust email sender with retry logic using Brevo transactional API."""

    def __init__(self):
        settings = get_settings()
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.brevo_api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        self.sender_email = settings.sender_email
        self.sender_name = settings.sender_name
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay_seconds

    @staticmethod
    def _validate_email(email: str) -> bool:
        """Basic email format validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    def send_digest_email(
        self,
        to_email: str,
        pdf_bytes: bytes,
        job_count: int,
        digest_date: Optional[date] = None,
    ) -> bool:
        """Send the nightly PDF digest email with attachment.

        Args:
            to_email: Recipient email address.
            pdf_bytes: The generated PDF as bytes.
            job_count: Number of jobs in the digest (for email body).
            digest_date: Date of the digest. Defaults to today.

        Returns:
            True if email was sent successfully, False otherwise.
        """
        if not self._validate_email(to_email):
            logger.error(f"Invalid recipient email: {to_email}")
            return False

        if digest_date is None:
            digest_date = date.today()

        date_str = digest_date.strftime("%d %b %Y")
        date_str_file = digest_date.strftime("%Y-%m-%d")

        subject = f"📋 JobScout Digest — {date_str} ({job_count} Jobs)"

        html_content = self._build_digest_html(job_count, date_str)

        # Encode PDF as base64 for attachment
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email.strip()}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject=subject,
            html_content=html_content,
            attachment=[{
                "content": pdf_base64,
                "name": f"JobScout_Digest_{date_str_file}.pdf",
                "type": "application/pdf",
            }],
        )

        return self._send_with_retry(send_smtp_email, "digest")

    def send_reminder_email(
        self,
        to_email: str,
        job_title: str,
        organization: str,
        exam: str,
        last_date_str: str,
        apply_link: str,
        days_left: int,
        reminder_type: str,
    ) -> bool:
        """Send a deadline reminder email (no PDF attachment).

        Args:
            to_email: Recipient email address.
            job_title: Job title.
            organization: Organization name.
            exam: Exam name or "Application".
            last_date_str: Formatted last date string.
            apply_link: Application URL.
            days_left: Number of days until deadline.
            reminder_type: "3_days" | "1_day" | "today"

        Returns:
            True if sent successfully.
        """
        if not self._validate_email(to_email):
            logger.error(f"Invalid recipient email: {to_email}")
            return False

        urgency_map = {
            "3_days": ("⏰ 3 Days Left", "#e37400"),
            "1_day": ("⚠️ 1 Day Left", "#c5221f"),
            "today": ("🔥 Last Day Today!", "#c5221f"),
        }
        header, color = urgency_map.get(reminder_type, ("⏰ Deadline Reminder", "#e37400"))

        subject = f"{header} — {job_title} @ {organization}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa;">
            <div style="background: white; border-radius: 12px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h1 style="color: {color}; font-size: 22px; margin-bottom: 20px; text-align: center;">{header}</h1>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px 0; color: #5f6368; font-weight: bold;">📌 Post</td><td style="padding: 8px 0;">{job_title}</td></tr>
                    <tr><td style="padding: 8px 0; color: #5f6368; font-weight: bold;">🏢 Organization</td><td style="padding: 8px 0;">{organization}</td></tr>
                    <tr><td style="padding: 8px 0; color: #5f6368; font-weight: bold;">📝 Exam</td><td style="padding: 8px 0;">{exam}</td></tr>
                    <tr><td style="padding: 8px 0; color: #5f6368; font-weight: bold;">📅 Last Date</td><td style="padding: 8px 0; color: {color}; font-weight: bold;">{last_date_str}</td></tr>
                </table>
                {"<a href='" + apply_link + "' style='display: inline-block; margin-top: 20px; padding: 12px 28px; background: #1a73e8; color: white; text-decoration: none; border-radius: 6px; font-weight: bold;'>Apply Now →</a>" if apply_link else ""}
            </div>
            <p style="text-align: center; color: #5f6368; font-size: 11px; margin-top: 15px;">
                Sent by JobScout Bot • Don't miss it! 🚀
            </p>
        </body>
        </html>
        """

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email.strip()}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject=subject,
            html_content=html_content,
        )

        return self._send_with_retry(send_smtp_email, f"reminder-{reminder_type}")

    def _build_digest_html(self, job_count: int, date_str: str) -> str:
        """Build the HTML email body for the digest (PDF is the attachment)."""
        if job_count == 0:
            summary = "No matching government jobs were found today."
            cta = "Don't worry — JobScout is monitoring 4 portals around the clock."
        else:
            summary = f"<b>{job_count}</b> matching government job{'s' if job_count != 1 else ''} found today."
            cta = "📎 <b>Open the attached PDF</b> for detailed descriptions of all jobs."

        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa;">
            <div style="background: white; border-radius: 12px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h1 style="color: #1a73e8; text-align: center; font-size: 24px; margin-bottom: 5px;">
                    📋 JobScout Daily Digest
                </h1>
                <p style="text-align: center; color: #5f6368; font-size: 13px; margin-bottom: 25px;">
                    {date_str}
                </p>
                <hr style="border: none; border-top: 2px solid #1a73e8; margin-bottom: 25px;">
                <p style="font-size: 16px; color: #202124; text-align: center; line-height: 1.6;">
                    {summary}
                </p>
                <p style="font-size: 14px; color: #5f6368; text-align: center; margin-top: 20px;">
                    {cta}
                </p>
            </div>
            <p style="text-align: center; color: #5f6368; font-size: 11px; margin-top: 15px;">
                Sources: NCS.gov.in • SarkariResult.com • FreeJobAlert.com • EmploymentNews.gov.in<br>
                Generated by JobScout Bot
            </p>
        </body>
        </html>
        """

    def _send_with_retry(self, email: sib_api_v3_sdk.SendSmtpEmail, label: str) -> bool:
        """Send email with exponential backoff retry."""
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.api_instance.send_transac_email(email)
                logger.info(f"📧 [{label}] Email sent successfully. Message ID: {response.message_id}")
                return True
            except ApiException as e:
                logger.error(f"📧 [{label}] Brevo API error (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    wait = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {wait}s...")
                    time.sleep(wait)
            except Exception as e:
                logger.error(f"📧 [{label}] Unexpected error (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    wait = self.retry_delay * (2 ** (attempt - 1))
                    time.sleep(wait)

        logger.error(f"📧 [{label}] All {self.max_retries} email send attempts failed.")
        return False
