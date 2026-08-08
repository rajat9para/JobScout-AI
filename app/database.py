"""Supabase database operations with retry logic and graceful error handling.

Every method returns a safe default on failure so the bot never crashes
because of a transient DB issue.
"""
import logging
import time
from typing import Optional, List
from supabase import create_client, Client
from app.config import get_settings
from app.models import Profile, Job, Alert, ExamReminder

logger = logging.getLogger(__name__)


class Database:
    """Thread-safe Supabase wrapper with automatic retries."""

    def __init__(self):
        settings = get_settings()
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay_seconds

    # ── Retry Decorator ──
    def _retry(self, operation, *args, **kwargs):
        """Execute a DB operation with exponential backoff retry."""
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"DB attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
        logger.error(f"DB operation failed after {self.max_retries} attempts: {last_exception}")
        return None

    # ── Profile Operations ──

    def get_profile_by_whatsapp(self, whatsapp_number: str) -> Optional[Profile]:
        """Fetch profile by WhatsApp number. Strips 'whatsapp:' prefix."""
        phone = whatsapp_number.replace("whatsapp:", "").strip()

        def _fetch():
            result = (
                self.client.table("profiles")
                .select("*")
                .eq("whatsapp_number", phone)
                .execute()
            )
            return Profile(**result.data[0]) if result.data else None

        return self._retry(_fetch)

    def create_profile(self, whatsapp_number: str) -> Optional[Profile]:
        """Create a new profile for a first-time user."""
        phone = whatsapp_number.replace("whatsapp:", "").strip()

        def _create():
            result = (
                self.client.table("profiles")
                .insert({
                    "whatsapp_number": phone,
                    "onboarding_state": "welcome",
                    "status": "active",
                    "alert_mode": "instant"
                })
                .execute()
            )
            return Profile(**result.data[0]) if result.data else None

        return self._retry(_create)

    def update_profile(self, whatsapp_number: str, updates: dict) -> bool:
        """Update profile fields. Returns True on success."""
        phone = whatsapp_number.replace("whatsapp:", "").strip()

        def _update():
            self.client.table("profiles").update(updates).eq("whatsapp_number", phone).execute()
            return True

        return self._retry(_update) or False

    # ── Job Operations ──

    def job_exists(self, raw_hash: str) -> bool:
        """Check deduplication hash. Returns True (exists) on DB failure to prevent duplicates."""
        def _check():
            result = (
                self.client.table("jobs")
                .select("id")
                .eq("raw_hash", raw_hash)
                .execute()
            )
            return len(result.data) > 0

        result = self._retry(_check)
        return result if result is not None else True  # Fail-safe: assume exists

    def save_job(self, job: Job) -> Optional[str]:
        """Save a new job. Returns the job ID or None."""
        def _save():
            data = job.model_dump(exclude={"id", "created_at"}, exclude_none=True)
            if data.get("last_date"):
                data["last_date"] = str(data["last_date"])
            if data.get("degree_tags"):
                data["degree_tags"] = data["degree_tags"]

            result = self.client.table("jobs").insert(data).execute()
            return result.data[0]["id"] if result.data else None

        return self._retry(_save)

    def get_recent_jobs(self, hours: int = 24) -> List[Job]:
        """Get jobs scraped within last N hours."""
        def _fetch():
            from datetime import datetime, timedelta, timezone
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            result = (
                self.client.table("jobs")
                .select("*")
                .gte("scraped_at", cutoff)
                .order("scraped_at", desc=True)
                .execute()
            )
            return [Job(**row) for row in result.data]

        result = self._retry(_fetch)
        return result if result is not None else []

    def get_jobs_by_deadline(self, days: int = 3) -> List[Job]:
        """Get jobs whose last_date is within N days. For exam reminders."""
        def _fetch():
            from datetime import date, timedelta
            target = (date.today() + timedelta(days=days)).isoformat()
            result = (
                self.client.table("jobs")
                .select("*")
                .eq("last_date", target)
                .execute()
            )
            return [Job(**row) for row in result.data]

        result = self._retry(_fetch)
        return result if result is not None else []

    # ── Alert Operations ──

    def record_alert(self, job_id: str) -> bool:
        def _record():
            self.client.table("sent_alerts").insert({"job_id": job_id}).execute()
            return True
        return self._retry(_record) or False

    def alert_exists(self, job_id: str) -> bool:
        def _check():
            result = (
                self.client.table("sent_alerts")
                .select("id")
                .eq("job_id", job_id)
                .execute()
            )
            return len(result.data) > 0
        result = self._retry(_check)
        return result if result is not None else True

    # ── Exam Reminder Operations ──

    def reminder_exists(self, job_id: str, reminder_type: str) -> bool:
        def _check():
            result = (
                self.client.table("exam_reminders")
                .select("id")
                .eq("job_id", job_id)
                .eq("reminder_type", reminder_type)
                .execute()
            )
            return len(result.data) > 0
        result = self._retry(_check)
        return result if result is not None else True

    def record_reminder(self, job_id: str, reminder_type: str) -> bool:
        def _record():
            self.client.table("exam_reminders").insert({
                "job_id": job_id,
                "reminder_type": reminder_type
            }).execute()
            return True
        return self._retry(_record) or False

    # ── Storage (Resume) ──

    def upload_resume(self, file_path: str, file_bytes: bytes, content_type: str = "application/pdf") -> Optional[str]:
        """Upload resume to Supabase Storage. Returns public URL."""
        def _upload():
            self.client.storage.from_("resumes").upload(
                file_path,
                file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            return self.client.storage.from_("resumes").get_public_url(file_path)
        return self._retry(_upload)

    def download_resume(self, file_path: str) -> Optional[bytes]:
        """Download resume bytes from Supabase Storage."""
        def _download():
            return self.client.storage.from_("resumes").download(file_path)
        return self._retry(_download)
