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
import os
from datetime import date, datetime
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── Premium Email Design System ──
# Consistent branding across all email types
_FONT_STACK = "'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
_BG_COLOR = "#0f0f1a"
_CARD_BG = "#1a1a2e"
_CARD_BORDER = "#2a2a4a"
_ACCENT = "#6C8FFF"
_ACCENT_BRIGHT = "#8BABFF"
_GREEN = "#34D399"
_GREEN_DARK = "#059669"
_RED = "#F87171"
_ORANGE = "#FBBF24"
_TEXT = "#F8FAFC"
_TEXT_DIM = "#94A3B8"
_TEXT_MUTED = "#64748B"


def _email_wrapper(inner_html: str, preheader: str = "") -> str:
    """Wrap email content in the premium dark-theme shell with Google Fonts."""
    return f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>JobScout</title>
    <!--[if mso]><style>body,table,td{{font-family:Arial,Helvetica,sans-serif!important}}</style><![endif]-->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    </style>
</head>
<body style="margin:0;padding:0;background:{_BG_COLOR};font-family:{_FONT_STACK};-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;">
    <!-- Preheader text (hidden, shows in email preview) -->
    <div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{preheader}</div>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{_BG_COLOR};">
        <tr><td align="center" style="padding:32px 16px;">
            <table role="presentation" width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%;">
                {inner_html}
            </table>

            <!-- Footer -->
            <table role="presentation" width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%;">
                <tr><td style="padding:24px 0 8px;text-align:center;">
                    <p style="margin:0;font-size:11px;color:{_TEXT_MUTED};letter-spacing:0.5px;line-height:1.6;">
                        JobScout v2.2 &bull; Your Personal Government Job Alert Bot<br>
                        Sources: NCS.gov.in &bull; SarkariResult &bull; FreeJobAlert &bull; EmploymentNews
                    </p>
                </td></tr>
            </table>
        </td></tr>
    </table>
</body>
</html>"""


class BrevoMailer:
    """Robust email sender with retry logic using Brevo transactional API."""

    def __init__(self):
        settings = get_settings()
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.brevo_api_key
        self.api_client = sib_api_v3_sdk.ApiClient(configuration)
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(self.api_client)
        self.sender_email = settings.sender_email
        self.sender_name = settings.sender_name
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay_seconds
        self.last_error = None  # Store last error for dashboard reporting

    def verify_connection(self) -> dict:
        """Verify Brevo API key, account status, and sender verification.

        Returns a dict with:
            ok: bool — True if everything is working
            account: str — Account email
            plan: str — Current plan type
            credits: int — Daily email credits remaining
            sender_verified: bool — Whether sender email is verified
            error: str — Error message if not ok
        """
        result = {"ok": False, "account": "", "plan": "", "credits": 0,
                  "sender_verified": False, "error": ""}
        try:
            # Check account
            account_api = sib_api_v3_sdk.AccountApi(self.api_client)
            account = account_api.get_account()
            result["account"] = account.email or ""
            if account.plan and len(account.plan) > 0:
                result["plan"] = account.plan[0].get("type", "unknown") if isinstance(account.plan[0], dict) else getattr(account.plan[0], "type", "unknown")
                result["credits"] = account.plan[0].get("credits", 0) if isinstance(account.plan[0], dict) else getattr(account.plan[0], "credits", 0)
        except ApiException as e:
            body = str(e.body) if e.body else str(e)
            if "unauthorized" in body.lower() or "unrecognised IP" in body:
                result["error"] = f"IP BLOCKED: Your IP is not authorized in Brevo. Go to https://app.brevo.com/security/authorised_ips and disable IP restriction. Raw: {body}"
            elif e.status == 401:
                result["error"] = f"INVALID API KEY: Your Brevo API key is invalid or expired. Generate a new one at https://app.brevo.com/settings/keys/api. Raw: {body}"
            else:
                result["error"] = f"Brevo API error (HTTP {e.status}): {body}"
            return result
        except Exception as e:
            result["error"] = f"Connection error: {str(e)}"
            return result

        # Check sender verification
        try:
            senders_api = sib_api_v3_sdk.SendersApi(self.api_client)
            senders = senders_api.get_senders()
            for s in (senders.senders or []):
                sender_email = s.get("email", "") if isinstance(s, dict) else getattr(s, "email", "")
                sender_active = s.get("active", False) if isinstance(s, dict) else getattr(s, "active", False)
                if sender_email.lower() == self.sender_email.lower() and sender_active:
                    result["sender_verified"] = True
                    break
            if not result["sender_verified"]:
                result["error"] = f"SENDER NOT VERIFIED: '{self.sender_email}' is not verified in Brevo. Go to https://app.brevo.com/senders/list to add and verify it."
                return result
        except Exception as e:
            logger.warning(f"Could not check senders (non-fatal): {e}")
            result["sender_verified"] = True  # Assume OK if we can't check

        result["ok"] = True
        return result

    @staticmethod
    def _validate_email(email: str) -> bool:
        """Basic email format validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    # ══════════════════════════════════════════════════════════
    #  TEST EMAIL
    # ══════════════════════════════════════════════════════════

    def send_test_email(self, to_email: str) -> bool:
        """Send a premium test email to verify Brevo integration is working."""
        if not self._validate_email(to_email):
            logger.error(f"Invalid test email: {to_email}")
            return False

        now = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

        inner = f"""
            <!-- Header with gradient -->
            <tr><td style="background:linear-gradient(135deg,#1e3a5f 0%,#2d1b69 50%,#1a1a2e 100%);border-radius:20px 20px 0 0;padding:40px 32px;text-align:center;">
                <div style="width:64px;height:64px;background:linear-gradient(135deg,{_ACCENT},{_GREEN});border-radius:16px;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;">
                    <span style="font-size:32px;line-height:64px;">🚀</span>
                </div>
                <h1 style="margin:0;font-size:26px;font-weight:800;color:{_TEXT};letter-spacing:-0.5px;">Email Service Active</h1>
                <p style="margin:12px 0 0;font-size:14px;color:{_TEXT_DIM};font-weight:500;">JobScout v2.2 &mdash; Connection Verified</p>
            </td></tr>

            <!-- Body -->
            <tr><td style="background:{_CARD_BG};padding:32px;border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};">
                <!-- Success Banner -->
                <div style="background:linear-gradient(135deg,rgba(52,211,153,0.1),rgba(52,211,153,0.05));border:1px solid rgba(52,211,153,0.2);border-radius:12px;padding:20px;margin-bottom:24px;text-align:center;">
                    <span style="font-size:28px;display:block;margin-bottom:8px;">✅</span>
                    <p style="margin:0;font-size:16px;font-weight:700;color:{_GREEN};">All Systems Operational</p>
                    <p style="margin:8px 0 0;font-size:13px;color:{_TEXT_DIM};">Your Brevo email integration is working perfectly.</p>
                </div>

                <!-- Info Grid -->
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.03);border-radius:12px;border:1px solid {_CARD_BORDER};">
                    <tr>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT_MUTED};font-weight:600;">📧 Recipient</td>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT};text-align:right;font-weight:500;">{to_email}</td>
                    </tr>
                    <tr>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT_MUTED};font-weight:600;">📬 Sender</td>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT};text-align:right;font-weight:500;">{self.sender_email}</td>
                    </tr>
                    <tr>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT_MUTED};font-weight:600;">🕐 Sent at</td>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT};text-align:right;font-weight:500;">{now}</td>
                    </tr>
                    <tr>
                        <td style="padding:16px 20px;font-size:13px;color:{_TEXT_MUTED};font-weight:600;">📅 Schedule</td>
                        <td style="padding:16px 20px;font-size:13px;color:{_ACCENT_BRIGHT};text-align:right;font-weight:600;">10 AM & 6 PM IST Daily</td>
                    </tr>
                </table>
            </td></tr>

            <!-- Bottom accent -->
            <tr><td style="background:{_CARD_BG};border-radius:0 0 20px 20px;border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};border-bottom:1px solid {_CARD_BORDER};padding:20px 32px;text-align:center;">
                <p style="margin:0;font-size:12px;color:{_TEXT_MUTED};">
                    PDF digest emails with matched government jobs will be delivered to this address.
                </p>
            </td></tr>
        """

        html = _email_wrapper(inner, preheader="Your JobScout email service is verified and working!")

        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email, "name": "JobScout User"}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject="✅ JobScout — Email Service Verified & Working!",
            html_content=html,
        )

        return self._send_with_retry(email, "test-email")

    # ══════════════════════════════════════════════════════════
    #  DIGEST EMAIL (with PDF attachment)
    # ══════════════════════════════════════════════════════════

    def send_digest_email(
        self,
        to_email: str,
        pdf_bytes: bytes,
        job_count: int,
        digest_date: Optional[date] = None,
    ) -> bool:
        """Send the PDF digest email with attachment."""
        if not self._validate_email(to_email):
            logger.error(f"Invalid recipient email: {to_email}")
            return False

        if digest_date is None:
            digest_date = date.today()

        date_str = digest_date.strftime("%d %b %Y")
        date_str_file = digest_date.strftime("%Y-%m-%d")
        day_name = digest_date.strftime("%A")

        subject = f"📋 JobScout Digest — {date_str} ({job_count} Jobs)"

        if job_count == 0:
            count_display = "0"
            summary = "No matching government jobs were found today."
            cta_text = "Don't worry — JobScout is monitoring 4 portals around the clock."
            badge_bg = f"rgba(251,191,36,0.1)"
            badge_border = f"rgba(251,191,36,0.3)"
            badge_color = _ORANGE
        else:
            count_display = str(job_count)
            summary = f"<strong>{job_count}</strong> matching government job{'s' if job_count != 1 else ''} found today."
            cta_text = "📎 Open the attached PDF for detailed descriptions, eligibility, salary, and apply links."
            badge_bg = f"rgba(52,211,153,0.1)"
            badge_border = f"rgba(52,211,153,0.3)"
            badge_color = _GREEN

        inner = f"""
            <!-- Header -->
            <tr><td style="background:linear-gradient(135deg,#0f2027 0%,#203a43 50%,#2c5364 100%);border-radius:20px 20px 0 0;padding:40px 32px;text-align:center;">
                <div style="width:56px;height:56px;background:linear-gradient(135deg,{_ACCENT},#a78bfa);border-radius:14px;margin:0 auto 20px;display:flex;align-items:center;justify-content:center;">
                    <span style="font-size:28px;line-height:56px;">📋</span>
                </div>
                <h1 style="margin:0;font-size:28px;font-weight:800;color:{_TEXT};letter-spacing:-0.5px;">JobScout Digest</h1>
                <div style="margin-top:16px;display:inline-block;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:50px;padding:8px 24px;">
                    <span style="font-size:13px;font-weight:600;color:{_TEXT_DIM};text-transform:uppercase;letter-spacing:1.5px;">{day_name}, {date_str}</span>
                </div>
            </td></tr>

            <!-- Stats Bar -->
            <tr><td style="background:{_CARD_BG};border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};padding:24px 32px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td width="33%" style="text-align:center;padding:16px 8px;background:rgba(108,143,255,0.06);border-radius:12px;">
                            <div style="font-size:32px;font-weight:800;color:{_ACCENT_BRIGHT};letter-spacing:-1px;">{count_display}</div>
                            <div style="font-size:10px;color:{_TEXT_MUTED};text-transform:uppercase;letter-spacing:1.5px;margin-top:4px;font-weight:600;">Jobs Found</div>
                        </td>
                        <td width="5%">&nbsp;</td>
                        <td width="28%" style="text-align:center;padding:16px 8px;background:rgba(108,143,255,0.06);border-radius:12px;">
                            <div style="font-size:32px;font-weight:800;color:{_ACCENT_BRIGHT};letter-spacing:-1px;">4</div>
                            <div style="font-size:10px;color:{_TEXT_MUTED};text-transform:uppercase;letter-spacing:1.5px;margin-top:4px;font-weight:600;">Sources</div>
                        </td>
                        <td width="5%">&nbsp;</td>
                        <td width="29%" style="text-align:center;padding:16px 8px;background:rgba(108,143,255,0.06);border-radius:12px;">
                            <div style="font-size:32px;font-weight:800;color:{_ACCENT_BRIGHT};letter-spacing:-1px;">📄</div>
                            <div style="font-size:10px;color:{_TEXT_MUTED};text-transform:uppercase;letter-spacing:1.5px;margin-top:4px;font-weight:600;">PDF Attached</div>
                        </td>
                    </tr>
                </table>
            </td></tr>

            <!-- Message -->
            <tr><td style="background:{_CARD_BG};border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};padding:0 32px 24px;">
                <div style="background:{badge_bg};border:1px solid {badge_border};border-radius:12px;padding:20px;text-align:center;">
                    <p style="margin:0;font-size:15px;color:{_TEXT};line-height:1.7;font-weight:500;">{summary}</p>
                    <p style="margin:12px 0 0;font-size:13px;color:{badge_color};font-weight:600;">{cta_text}</p>
                </div>
            </td></tr>

            <!-- Footer -->
            <tr><td style="background:{_CARD_BG};border-radius:0 0 20px 20px;border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};border-bottom:1px solid {_CARD_BORDER};padding:20px 32px;text-align:center;">
                <p style="margin:0;font-size:12px;color:{_TEXT_MUTED};">
                    Sent to: {to_email} &bull; Next digest at {'6:00 PM' if datetime.now().hour < 15 else '10:00 AM'} IST
                </p>
            </td></tr>
        """

        html = _email_wrapper(inner, preheader=f"{job_count} government jobs found today — open attached PDF for details")

        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email.strip()}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject=subject,
            html_content=html,
            attachment=[{
                "content": pdf_base64,
                "name": f"JobScout_Digest_{date_str_file}.pdf",
                "type": "application/pdf",
            }],
        )

        return self._send_with_retry(send_smtp_email, "digest")

    # ══════════════════════════════════════════════════════════
    #  REMINDER EMAIL
    # ══════════════════════════════════════════════════════════

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
        """Send a deadline reminder email (no PDF attachment)."""
        if not self._validate_email(to_email):
            logger.error(f"Invalid recipient email: {to_email}")
            return False

        urgency_map = {
            "3_days": ("⏰ 3 Days Left", _ORANGE, "rgba(251,191,36,0.1)", "rgba(251,191,36,0.3)"),
            "1_day":  ("⚠️ 1 Day Left", _RED, "rgba(248,113,113,0.1)", "rgba(248,113,113,0.3)"),
            "today":  ("🔥 Last Day!", _RED, "rgba(248,113,113,0.15)", "rgba(248,113,113,0.4)"),
        }
        header, color, bg, border = urgency_map.get(
            reminder_type, ("⏰ Deadline Reminder", _ORANGE, "rgba(251,191,36,0.1)", "rgba(251,191,36,0.3)")
        )

        subject = f"{header} — {job_title} @ {organization}"

        apply_btn = ""
        if apply_link:
            apply_btn = f"""
                <tr><td style="padding:0 32px 24px;background:{_CARD_BG};border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};text-align:center;">
                    <a href="{apply_link}" style="display:inline-block;padding:14px 40px;background:linear-gradient(135deg,{_ACCENT},#a78bfa);color:white;text-decoration:none;border-radius:12px;font-weight:700;font-size:15px;letter-spacing:0.3px;">Apply Now &rarr;</a>
                </td></tr>
            """

        inner = f"""
            <!-- Urgency Header -->
            <tr><td style="background:linear-gradient(135deg,#1a0000 0%,#2d1b1b 50%,#1a1a2e 100%);border-radius:20px 20px 0 0;padding:36px 32px;text-align:center;">
                <div style="font-size:40px;margin-bottom:12px;">{header.split(' ')[0]}</div>
                <h1 style="margin:0;font-size:24px;font-weight:800;color:{color};letter-spacing:-0.3px;">{header}</h1>
                <p style="margin:10px 0 0;font-size:13px;color:{_TEXT_DIM};">Application Deadline Reminder</p>
            </td></tr>

            <!-- Job Details -->
            <tr><td style="background:{_CARD_BG};border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};padding:24px 32px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.03);border-radius:12px;border:1px solid {_CARD_BORDER};">
                    <tr>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT_MUTED};font-weight:600;">📌 Post</td>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:14px;color:{_TEXT};text-align:right;font-weight:700;">{job_title}</td>
                    </tr>
                    <tr>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT_MUTED};font-weight:600;">🏢 Organization</td>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT};text-align:right;font-weight:500;">{organization}</td>
                    </tr>
                    <tr>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT_MUTED};font-weight:600;">📝 Exam</td>
                        <td style="padding:16px 20px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT};text-align:right;font-weight:500;">{exam}</td>
                    </tr>
                    <tr>
                        <td style="padding:16px 20px;font-size:13px;color:{_TEXT_MUTED};font-weight:600;">📅 Last Date</td>
                        <td style="padding:16px 20px;font-size:14px;color:{color};text-align:right;font-weight:800;">{last_date_str}</td>
                    </tr>
                </table>
            </td></tr>

            <!-- Apply Button -->
            {apply_btn}

            <!-- Footer -->
            <tr><td style="background:{_CARD_BG};border-radius:0 0 20px 20px;border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};border-bottom:1px solid {_CARD_BORDER};padding:20px 32px;text-align:center;">
                <p style="margin:0;font-size:12px;color:{_TEXT_MUTED};">
                    JobScout Bot &bull; Smart Deadline Alerts
                </p>
            </td></tr>
        """

        html = _email_wrapper(inner, preheader=f"{header} — {job_title} at {organization}. Apply before {last_date_str}!")

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email.strip()}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject=subject,
            html_content=html,
        )

        return self._send_with_retry(send_smtp_email, f"reminder-{reminder_type}")

    # ══════════════════════════════════════════════════════════
    #  SEND WITH RETRY
    # ══════════════════════════════════════════════════════════

    def _send_with_retry(self, email: sib_api_v3_sdk.SendSmtpEmail, label: str) -> bool:
        """Send email with exponential backoff retry."""
        self.last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.api_instance.send_transac_email(email)
                logger.info(f"📧 [{label}] Email sent successfully. Message ID: {response.message_id}")
                return True
            except ApiException as e:
                body = str(e.body) if e.body else str(e)
                logger.error(f"📧 [{label}] Brevo API error (attempt {attempt}/{self.max_retries}): {body}")
                # Parse specific error types for user-friendly messages
                if "unrecognised IP" in body or "unauthorized" in body.lower():
                    self.last_error = "IP_BLOCKED: Your IP is not authorized in Brevo. Disable IP restriction at https://app.brevo.com/security/authorised_ips"
                elif e.status == 401:
                    self.last_error = "INVALID_API_KEY: Brevo API key is invalid or expired. Check .env file."
                elif "not found" in body.lower() and "sender" in body.lower():
                    self.last_error = "SENDER_NOT_VERIFIED: Sender email not verified in Brevo. Verify at https://app.brevo.com/senders/list"
                elif e.status == 429:
                    self.last_error = "RATE_LIMITED: Brevo daily email limit reached (300/day on free plan). Try again tomorrow."
                else:
                    self.last_error = f"BREVO_ERROR ({e.status}): {body[:200]}"
                if attempt < self.max_retries:
                    wait = self.retry_delay * (2 ** (attempt - 1))
                    logger.info(f"Retrying in {wait}s...")
                    time.sleep(wait)
            except Exception as e:
                self.last_error = f"UNEXPECTED: {str(e)[:200]}"
                logger.error(f"📧 [{label}] Unexpected error (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    wait = self.retry_delay * (2 ** (attempt - 1))
                    time.sleep(wait)

        logger.error(f"📧 [{label}] All {self.max_retries} email send attempts failed. Last error: {self.last_error}")
        return False
