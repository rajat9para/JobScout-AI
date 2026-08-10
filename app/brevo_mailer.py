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

    @staticmethod
    def _get_logo_base64() -> str:
        """Read static/weblogo.png and return a Base64 data URI."""
        import os, base64
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "weblogo.png")
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception as e:
            logger.error(f"Failed to load logo: {e}")
        return ""

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

        logo_uri = self._get_logo_base64()
        logo_html = f'<img src="{logo_uri}" alt="JobScout Logo" style="width: 48px; height: 48px; display: block; margin: 0 auto 15px; border-radius: 12px; border: 2px solid #1a73e8; box-shadow: 0 4px 12px rgba(26,115,232,0.2);">' if logo_uri else ''

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f0f2f5;">
            <div style="background: white; border-radius: 16px; padding: 35px 30px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); border-top: 5px solid {color};">
                {logo_html}
                <h1 style="color: {color}; font-size: 22px; margin: 0 0 20px; text-align: center;">{header}</h1>
                <div style="background: #f8f9fa; border-radius: 10px; padding: 20px; border: 1px solid #e9ecef; margin-bottom: 25px;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr><td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #64748b; font-weight: 600;" width="35%">📌 Post</td><td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #1e293b; font-weight: 700;">{job_title}</td></tr>
                        <tr><td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #64748b; font-weight: 600;">🏢 Organization</td><td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #1e293b;">{organization}</td></tr>
                        <tr><td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #64748b; font-weight: 600;">📝 Exam</td><td style="padding: 10px 0; border-bottom: 1px solid #eee; color: #1e293b;">{exam}</td></tr>
                        <tr><td style="padding: 10px 0; color: #64748b; font-weight: 600;">📅 Last Date</td><td style="padding: 10px 0; color: {color}; font-weight: 700;">{last_date_str}</td></tr>
                    </table>
                </div>
                {"<div style='text-align: center;'><a href='" + apply_link + "' style='display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #1a73e8, #4285f4); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 15px; box-shadow: 0 4px 12px rgba(26,115,232,0.3);'>Apply Now &rarr;</a></div>" if apply_link else ""}
            </div>
            <p style="text-align: center; color: #94a3b8; font-size: 12px; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px;">
                JobScout Bot &bull; Smart Job Alerts
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

        logo_uri = self._get_logo_base64()
        logo_html = f'<img src="{logo_uri}" alt="JobScout Logo" style="width: 56px; height: 56px; display: inline-block; vertical-align: middle; margin-right: 12px; border-radius: 12px; border: 2px solid #1a73e8; box-shadow: 0 4px 12px rgba(26,115,232,0.2);">' if logo_uri else ''

        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f0f2f5;">
            <div style="background: white; border-radius: 16px; padding: 35px 30px; box-shadow: 0 4px 24px rgba(0,0,0,0.06); border-top: 5px solid #1a73e8;">
                <div style="text-align: center; margin-bottom: 25px;">
                    {logo_html}
                    <h1 style="color: #1e293b; display: inline-block; vertical-align: middle; font-size: 26px; margin: 0;">JobScout Digest</h1>
                </div>
                <div style="background: #f8f9fa; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 25px; border: 1px solid #e9ecef;">
                    <span style="color: #64748b; font-size: 14px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">{date_str}</span>
                </div>
                <p style="font-size: 17px; color: #334155; text-align: center; line-height: 1.6; font-weight: 500;">
                    {summary}
                </p>
                <div style="text-align: center; margin-top: 30px;">
                    <p style="font-size: 15px; color: #1a73e8; font-weight: 600; padding: 15px; background: rgba(26,115,232,0.05); border-radius: 8px;">
                        {cta}
                    </p>
                </div>
            </div>
            <p style="text-align: center; color: #94a3b8; font-size: 11px; margin-top: 20px; text-transform: uppercase; letter-spacing: 1px;">
                Sources: NCS.gov.in &bull; SarkariResult &bull; FreeJobAlert &bull; EmploymentNews<br><br>
                JobScout Bot v2.2
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

    def send_test_email(self, to_email: str) -> bool:
        """Send a test email to verify Brevo integration is working."""
        if not self._validate_email(to_email):
            logger.error(f"Invalid test email: {to_email}")
            return False

        from datetime import datetime
        now = datetime.now().strftime("%d %b %Y, %I:%M %p")

        logo_uri = self._get_logo_base64()
        logo_html = f'<img src="{logo_uri}" alt="JobScout Logo" style="width: 48px; height: 48px; display: block; margin: 0 auto 15px; border-radius: 12px; border: 2px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">' if logo_uri else ''

        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email, "name": "JobScout User"}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject="✅ JobScout — Email Service Test Successful!",
            html_content=f"""
            <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; padding: 40px 20px; margin: 0;">
                <div style="max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 16px; 
                            box-shadow: 0 4px 24px rgba(0,0,0,0.08); overflow: hidden;">
                    <div style="background: linear-gradient(135deg, #1a73e8 0%, #764ba2 100%); 
                                padding: 35px 28px; text-align: center;">
                        {logo_html}
                        <h1 style="color: white; margin: 0; font-size: 24px;">✅ Email Service Working!</h1>
                        <p style="color: rgba(255,255,255,0.85); margin: 10px 0 0; font-size: 14px;">
                            JobScout v2.2 — Mail Verification
                        </p>
                    </div>
                    <div style="padding: 30px;">
                        <p style="color: #334155; font-size: 15px; line-height: 1.7;">
                            Great news! Your <strong>Brevo email integration</strong> is correctly verified and working.
                        </p>
                        <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 16px; 
                                    border-radius: 8px; margin: 20px 0;">
                            <strong style="color: #166534;">🎉 All Systems Operational</strong><br>
                            <span style="color: #15803d; font-size: 13px;">
                                PDF digest emails will be delivered to this address at 10 AM and 6 PM IST daily.
                            </span>
                        </div>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
                            <table style="width: 100%; font-size: 13px; color: #64748b;">
                                <tr><td style="padding: 6px 0; font-weight: 600;">📧 Recipient:</td><td style="text-align:right;">{to_email}</td></tr>
                                <tr><td style="padding: 6px 0; font-weight: 600;">🕐 Sent at:</td><td style="text-align:right;">{now}</td></tr>
                                <tr><td style="padding: 6px 0; font-weight: 600;">📬 Sender:</td><td style="text-align:right;">{self.sender_email}</td></tr>
                            </table>
                        </div>
                    </div>
                    <div style="background: #f1f5f9; padding: 16px 28px; text-align: center;">
                        <p style="color: #94a3b8; font-size: 11px; margin: 0; text-transform: uppercase; letter-spacing: 1px;">
                            JobScout Bot &bull; Your Personal Alert Bot
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """,
        )

        return self._send_with_retry(email, "test-email")
