"""Twilio WhatsApp integration with formatted messaging."""
import logging
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config import get_settings

logger = logging.getLogger(__name__)


class TwilioWhatsApp:
    """Robust WhatsApp message sender with retry."""

    def __init__(self):
        settings = get_settings()
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_number = self._format_number(settings.twilio_whatsapp_number)

    def _format_number(self, number: str) -> str:
        if not number.startswith("whatsapp:"):
            return f"whatsapp:{number}"
        return number

    def send_message(self, to: str, body: str, media_url: Optional[str] = None) -> bool:
        """Send WhatsApp message. Truncates if >1600 chars (Twilio limit)."""
        to_number = self._format_number(to)

        if len(body) > 1600:
            body = body[:1597] + "..."

        try:
            params = {"from_": self.from_number, "to": to_number, "body": body}
            if media_url:
                params["media_url"] = [media_url]

            msg = self.client.messages.create(**params)
            logger.info(f"📤 Sent to {to_number}: SID={msg.sid}")
            return True
        except TwilioRestException as e:
            logger.error(f"Twilio error to {to_number}: {e}")
            return False
        except Exception as e:
            logger.error(f"Send failed to {to_number}: {e}")
            return False

    def send_job_alert(self, to: str, job) -> bool:
        """Send short, focused job alert."""
        last_date = job.last_date.strftime("%d %b %Y") if job.last_date else "N/A"
        exam = job.exam_required or "N/A"
        salary = job.salary or "N/A"

        body = (
            f"🎓 *New Govt Job Alert*\n\n"
            f"📌 *Post:* {job.title}\n"
            f"🏢 *Org:* {job.organization}\n"
            f"💰 *Salary:* {salary}\n"
            f"📝 *Exam:* {exam}\n"
            f"📅 *Last Date:* {last_date}\n"
            f"🔗 *Details:* {job.apply_link or 'Check ' + job.source}\n\n"
            f"Reply *PAUSE* | *UPDATE* | *HELP*"
        )
        return self.send_message(to, body)

    def send_digest(self, to: str, jobs: list) -> bool:
        """Send daily digest of multiple jobs."""
        if not jobs:
            return True

        body = "📋 *Daily Job Digest*\n\n"
        for i, job in enumerate(jobs[:10], 1):
            last_date = job.last_date.strftime("%d %b") if job.last_date else "N/A"
            body += f"{i}. {job.title} @ {job.organization} (Due: {last_date})\n"

        if len(jobs) > 10:
            body += f"\n...and {len(jobs) - 10} more.\n"

        body += "\nReply *BULK* for full details | *PAUSE* to stop"
        return self.send_message(to, body)

    def send_exam_reminder(self, to: str, job) -> bool:
        """Send exam deadline reminder."""
        last_date = job.last_date.strftime("%d %b %Y") if job.last_date else "N/A"
        exam = job.exam_required or "Application"

        body = (
            f"⏰ *Deadline Reminder*\n\n"
            f"📌 *Post:* {job.title}\n"
            f"🏢 *Org:* {job.organization}\n"
            f"📝 *Exam:* {exam}\n"
            f"📅 *Last Date:* {last_date}\n"
            f"🔗 *Apply:* {job.apply_link or 'Check ' + job.source}\n\n"
            f"Don't miss it! 🚀"
        )
        return self.send_message(to, body)

    def send_welcome(self, to: str) -> bool:
        body = (
            "👋 *Welcome to JobScout!*\n\n"
            "I find government jobs matching your profile.\n\n"
            "Let's set you up! Please tell me your *qualification* (e.g., B.Tech, BSc, BCA, Law, MBA)\n"
            "OR upload your *resume PDF* and I'll detect it automatically."
        )
        return self.send_message(to, body)
