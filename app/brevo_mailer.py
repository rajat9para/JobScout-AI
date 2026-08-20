"""Brevo (Sendinblue) transactional email client.

Handles sending the daily PDF report and deadline reminder emails.
Uses the official sib-api-v3-sdk Python SDK.

Brevo Free Tier: 300 emails/day, 9000 emails/month — more than enough
for a single-user daily digest.

Design: Professional "JobScout-AI" branding with clean dark theme.
"""
import base64
import logging
import time
import re
from datetime import date, datetime
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── Professional Email Design System ──
_FONT = "'Inter', 'Segoe UI', 'Roboto', -apple-system, BlinkMacSystemFont, Arial, sans-serif"
_BG = "#0B1120"
_CARD = "#111827"
_CARD_BORDER = "#1F2937"
_ACCENT = "#3B82F6"
_ACCENT_LIGHT = "#60A5FA"
_GREEN = "#10B981"
_RED = "#EF4444"
_AMBER = "#F59E0B"
_TEXT = "#F1F5F9"
_TEXT_DIM = "#94A3B8"
_TEXT_MUTED = "#64748B"


def _email_shell(content: str, preheader: str = "") -> str:
    """Wrap content in the professional email shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>JobScout-AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:0;background:{_BG};font-family:{_FONT};-webkit-font-smoothing:antialiased;">
    <div style="display:none;max-height:0;overflow:hidden;">{preheader}</div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{_BG};">
        <tr><td align="center" style="padding:32px 16px;">
            <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
                {content}
            </table>
            <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
                <tr><td style="padding:20px 0;text-align:center;">
                    <p style="margin:0;font-size:10px;color:{_TEXT_MUTED};letter-spacing:0.5px;line-height:1.6;">
                        JobScout-AI &bull; Government Job Intelligence<br>
                        Sources: SarkariResult &bull; FreeJobAlert &bull; SarkariExam &bull; RojgarResult
                    </p>
                </td></tr>
            </table>
        </td></tr>
    </table>
</body>
</html>"""


class BrevoMailer:
    """Email sender with retry logic using Brevo transactional API."""

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
        self.last_error = None

    def verify_connection(self) -> dict:
        """Verify Brevo API key, account status, and sender verification."""
        result = {"ok": False, "account": "", "plan": "", "credits": 0,
                  "sender_verified": False, "error": ""}
        try:
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
                result["error"] = f"SENDER NOT VERIFIED: '{self.sender_email}' is not verified in Brevo."
                return result
        except Exception as e:
            logger.warning(f"Could not check senders (non-fatal): {e}")
            result["sender_verified"] = True

        result["ok"] = True
        return result

    @staticmethod
    def _validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    # ══════════════════════════════════════════════════════════
    #  TEST EMAIL
    # ══════════════════════════════════════════════════════════

    def send_test_email(self, to_email: str) -> bool:
        """Send a test email to verify integration."""
        if not self._validate_email(to_email):
            logger.error(f"Invalid test email: {to_email}")
            return False

        now = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

        content = f"""
            <!-- Header -->
            <tr><td style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#1e293b 100%);border-radius:16px 16px 0 0;padding:36px 28px;text-align:center;">
                <div style="font-size:28px;margin-bottom:12px;">✅</div>
                <h1 style="margin:0;font-size:22px;font-weight:800;color:{_TEXT};letter-spacing:-0.3px;">JobScout-AI</h1>
                <p style="margin:8px 0 0;font-size:12px;color:{_TEXT_DIM};font-weight:500;text-transform:uppercase;letter-spacing:1.5px;">Email Service Verified</p>
            </td></tr>

            <!-- Body -->
            <tr><td style="background:{_CARD};padding:28px;border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};">
                <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:16px;text-align:center;margin-bottom:20px;">
                    <p style="margin:0;font-size:14px;font-weight:700;color:{_GREEN};">All Systems Operational</p>
                    <p style="margin:6px 0 0;font-size:12px;color:{_TEXT_DIM};">Email delivery is working correctly.</p>
                </div>

                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.02);border-radius:10px;border:1px solid {_CARD_BORDER};">
                    <tr>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT_MUTED};font-weight:600;">Recipient</td>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT};text-align:right;">{to_email}</td>
                    </tr>
                    <tr>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT_MUTED};font-weight:600;">Sent at</td>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT};text-align:right;">{now}</td>
                    </tr>
                    <tr>
                        <td style="padding:12px 16px;font-size:12px;color:{_TEXT_MUTED};font-weight:600;">Schedule</td>
                        <td style="padding:12px 16px;font-size:12px;color:{_ACCENT_LIGHT};text-align:right;font-weight:600;">10 AM &amp; 6 PM IST Daily</td>
                    </tr>
                </table>
            </td></tr>

            <!-- Footer -->
            <tr><td style="background:{_CARD};border-radius:0 0 16px 16px;border:1px solid {_CARD_BORDER};border-top:0;padding:16px 28px;text-align:center;">
                <p style="margin:0;font-size:11px;color:{_TEXT_MUTED};">
                    Your daily job report with PDF attachment will be sent to this address.
                </p>
            </td></tr>
        """

        html = _email_shell(content, preheader="JobScout-AI email service verified!")

        email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email, "name": "JobScout-AI User"}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject="✅ JobScout-AI — Email Verified",
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
        """Send the daily report email with PDF attachment."""
        if not self._validate_email(to_email):
            logger.error(f"Invalid recipient email: {to_email}")
            return False

        if digest_date is None:
            digest_date = date.today()

        date_str = digest_date.strftime("%d %b %Y")
        date_file = digest_date.strftime("%Y-%m-%d")
        day_name = digest_date.strftime("%A")

        subject = f"📋 JobScout-AI Report — {date_str} ({job_count} Jobs)"

        if job_count == 0:
            status_text = "No matching jobs found today."
            action_text = "JobScout-AI is monitoring 4 portals continuously. You'll be notified when new jobs match your profile."
            badge_bg = "rgba(249,115,22,0.08)"
            badge_border = "rgba(249,115,22,0.2)"
            badge_color = _AMBER
        else:
            status_text = f"<strong>{job_count}</strong> government job{'s' if job_count != 1 else ''} matched your profile."
            action_text = "📎 Open the attached PDF for the complete report with job details, eligibility, salary, and apply links."
            badge_bg = "rgba(16,185,129,0.08)"
            badge_border = "rgba(16,185,129,0.2)"
            badge_color = _GREEN

        content = f"""
            <!-- Header -->
            <tr><td style="background:linear-gradient(135deg,#0f172a 0%,#1B2A4A 50%,#1e293b 100%);border-radius:16px 16px 0 0;padding:36px 28px;text-align:center;">
                <h1 style="margin:0;font-size:24px;font-weight:800;color:{_TEXT};letter-spacing:-0.3px;">JobScout-AI</h1>
                <p style="margin:6px 0 0;font-size:11px;color:{_TEXT_DIM};font-weight:600;text-transform:uppercase;letter-spacing:2px;">Daily Job Report</p>
                <div style="margin-top:14px;display:inline-block;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:40px;padding:6px 20px;">
                    <span style="font-size:12px;font-weight:600;color:{_TEXT_DIM};letter-spacing:1px;">{day_name}, {date_str}</span>
                </div>
            </td></tr>

            <!-- Stats -->
            <tr><td style="background:{_CARD};border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};padding:20px 28px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td width="30%" style="text-align:center;padding:14px 4px;background:rgba(59,130,246,0.05);border-radius:10px;">
                            <div style="font-size:28px;font-weight:800;color:{_ACCENT_LIGHT};letter-spacing:-1px;">{job_count}</div>
                            <div style="font-size:9px;color:{_TEXT_MUTED};text-transform:uppercase;letter-spacing:1.5px;margin-top:4px;font-weight:600;">Jobs</div>
                        </td>
                        <td width="5%">&nbsp;</td>
                        <td width="30%" style="text-align:center;padding:14px 4px;background:rgba(59,130,246,0.05);border-radius:10px;">
                            <div style="font-size:28px;font-weight:800;color:{_ACCENT_LIGHT};letter-spacing:-1px;">4</div>
                            <div style="font-size:9px;color:{_TEXT_MUTED};text-transform:uppercase;letter-spacing:1.5px;margin-top:4px;font-weight:600;">Sources</div>
                        </td>
                        <td width="5%">&nbsp;</td>
                        <td width="30%" style="text-align:center;padding:14px 4px;background:rgba(59,130,246,0.05);border-radius:10px;">
                            <div style="font-size:28px;font-weight:800;color:{_ACCENT_LIGHT};">📄</div>
                            <div style="font-size:9px;color:{_TEXT_MUTED};text-transform:uppercase;letter-spacing:1.5px;margin-top:4px;font-weight:600;">PDF Report</div>
                        </td>
                    </tr>
                </table>
            </td></tr>

            <!-- Status Message -->
            <tr><td style="background:{_CARD};border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};padding:0 28px 20px;">
                <div style="background:{badge_bg};border:1px solid {badge_border};border-radius:10px;padding:16px;text-align:center;">
                    <p style="margin:0;font-size:14px;color:{_TEXT};line-height:1.6;font-weight:500;">{status_text}</p>
                    <p style="margin:10px 0 0;font-size:12px;color:{badge_color};font-weight:600;">{action_text}</p>
                </div>
            </td></tr>

            <!-- Footer -->
            <tr><td style="background:{_CARD};border-radius:0 0 16px 16px;border:1px solid {_CARD_BORDER};border-top:0;padding:16px 28px;text-align:center;">
                <p style="margin:0;font-size:11px;color:{_TEXT_MUTED};">
                    Sent to {to_email} &bull; Next report at {'6:00 PM' if datetime.now().hour < 15 else '10:00 AM'} IST
                </p>
            </td></tr>
        """

        html = _email_shell(content, preheader=f"{job_count} government jobs found — see attached PDF report")

        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        send_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email.strip()}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject=subject,
            html_content=html,
            attachment=[{
                "content": pdf_b64,
                "name": f"JobScout-AI_Report_{date_file}.pdf",
                "type": "application/pdf",
            }],
        )

        return self._send_with_retry(send_email, "digest")

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
        """Send a deadline reminder email."""
        if not self._validate_email(to_email):
            logger.error(f"Invalid recipient email: {to_email}")
            return False

        urgency_map = {
            "3_days": ("⏰ 3 Days Left", _AMBER, "rgba(245,158,11,0.08)", "rgba(245,158,11,0.2)"),
            "1_day":  ("⚠️ 1 Day Left", _RED, "rgba(239,68,68,0.08)", "rgba(239,68,68,0.2)"),
            "today":  ("🔥 Last Day!", _RED, "rgba(239,68,68,0.12)", "rgba(239,68,68,0.3)"),
        }
        header, color, bg, border = urgency_map.get(
            reminder_type, ("⏰ Deadline Reminder", _AMBER, "rgba(245,158,11,0.08)", "rgba(245,158,11,0.2)")
        )

        subject = f"{header} — {job_title} @ {organization}"

        apply_btn = ""
        if apply_link:
            apply_btn = f"""
                <tr><td style="padding:0 28px 20px;background:{_CARD};border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};text-align:center;">
                    <a href="{apply_link}" style="display:inline-block;padding:12px 36px;background:{_ACCENT};color:white;text-decoration:none;border-radius:10px;font-weight:700;font-size:14px;">Apply Now →</a>
                </td></tr>
            """

        content = f"""
            <!-- Header -->
            <tr><td style="background:linear-gradient(135deg,#1a0505 0%,#2d1515 50%,#1e293b 100%);border-radius:16px 16px 0 0;padding:32px 28px;text-align:center;">
                <div style="font-size:36px;margin-bottom:10px;">{header.split(' ')[0]}</div>
                <h1 style="margin:0;font-size:20px;font-weight:800;color:{color};letter-spacing:-0.3px;">{header}</h1>
                <p style="margin:8px 0 0;font-size:11px;color:{_TEXT_DIM};text-transform:uppercase;letter-spacing:1.5px;">JobScout-AI • Deadline Alert</p>
            </td></tr>

            <!-- Details -->
            <tr><td style="background:{_CARD};border-left:1px solid {_CARD_BORDER};border-right:1px solid {_CARD_BORDER};padding:20px 28px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.02);border-radius:10px;border:1px solid {_CARD_BORDER};">
                    <tr>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT_MUTED};font-weight:600;">📌 Post</td>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:13px;color:{_TEXT};text-align:right;font-weight:700;">{job_title}</td>
                    </tr>
                    <tr>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT_MUTED};font-weight:600;">🏢 Organization</td>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT};text-align:right;">{organization}</td>
                    </tr>
                    <tr>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT_MUTED};font-weight:600;">📝 Exam</td>
                        <td style="padding:12px 16px;border-bottom:1px solid {_CARD_BORDER};font-size:12px;color:{_TEXT};text-align:right;">{exam}</td>
                    </tr>
                    <tr>
                        <td style="padding:12px 16px;font-size:12px;color:{_TEXT_MUTED};font-weight:600;">📅 Last Date</td>
                        <td style="padding:12px 16px;font-size:13px;color:{color};text-align:right;font-weight:800;">{last_date_str}</td>
                    </tr>
                </table>
            </td></tr>

            {apply_btn}

            <!-- Footer -->
            <tr><td style="background:{_CARD};border-radius:0 0 16px 16px;border:1px solid {_CARD_BORDER};border-top:0;padding:16px 28px;text-align:center;">
                <p style="margin:0;font-size:11px;color:{_TEXT_MUTED};">
                    JobScout-AI &bull; Smart Deadline Alerts
                </p>
            </td></tr>
        """

        html = _email_shell(content, preheader=f"{header} — {job_title} at {organization}. Apply before {last_date_str}!")

        send_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email.strip()}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject=subject,
            html_content=html,
        )

        return self._send_with_retry(send_email, f"reminder-{reminder_type}")

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
                if "unrecognised IP" in body or "unauthorized" in body.lower():
                    self.last_error = "IP_BLOCKED: Your IP is not authorized in Brevo. Disable IP restriction at https://app.brevo.com/security/authorised_ips"
                elif e.status == 401:
                    self.last_error = "INVALID_API_KEY: Brevo API key is invalid or expired."
                elif "not found" in body.lower() and "sender" in body.lower():
                    self.last_error = "SENDER_NOT_VERIFIED: Sender email not verified in Brevo."
                elif e.status == 429:
                    self.last_error = "RATE_LIMITED: Brevo daily email limit reached."
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
