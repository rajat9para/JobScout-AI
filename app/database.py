"""Supabase database operations with retry logic and graceful error handling.

Every method returns a safe default on failure so the bot never crashes
because of a transient DB issue.
"""
import logging
import time
from typing import Optional, List
from datetime import date, timedelta, datetime, timezone
from supabase import create_client, Client
from app.config import get_settings
from app.models import Profile, Job, Alert, ExamReminder, DigestEntry

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

    def get_profile_by_email(self, email: str) -> Optional[Profile]:
        """Fetch profile by email address."""
        email = email.strip().lower()

        def _fetch():
            result = (
                self.client.table("profiles")
                .select("*")
                .eq("email", email)
                .execute()
            )
            return Profile(**result.data[0]) if result.data else None

        return self._retry(_fetch)

    def get_first_active_profile(self) -> Optional[Profile]:
        """Fetch the first active profile (single-user mode)."""
        def _fetch():
            result = (
                self.client.table("profiles")
                .select("*")
                .eq("status", "active")
                .limit(1)
                .execute()
            )
            return Profile(**result.data[0]) if result.data else None

        return self._retry(_fetch)

    def create_profile(self, email: str, qualification: str,
                       interests: List[str], experience_level: str) -> Optional[Profile]:
        """Create a new profile."""
        email = email.strip().lower()

        def _create():
            result = (
                self.client.table("profiles")
                .insert({
                    "email": email,
                    "qualification": qualification,
                    "interests": interests,
                    "experience_level": experience_level,
                    "status": "active",
                })
                .execute()
            )
            return Profile(**result.data[0]) if result.data else None

        return self._retry(_create)

    def upsert_profile(self, email: str, qualification: str,
                       interests: List[str], experience_level: str) -> Optional[Profile]:
        """Create or update profile by email. Idempotent."""
        email = email.strip().lower()

        existing = self.get_profile_by_email(email)
        if existing:
            self.update_profile(email, {
                "qualification": qualification,
                "interests": interests,
                "experience_level": experience_level,
                "status": "active",
            })
            return self.get_profile_by_email(email)
        else:
            return self.create_profile(email, qualification, interests, experience_level)

    def update_profile(self, email: str, updates: dict) -> bool:
        """Update profile fields. Returns True on success."""
        email = email.strip().lower()

        def _update():
            self.client.table("profiles").update(updates).eq("email", email).execute()
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
            data = job.model_dump(exclude={"id", "created_at", "scraped_at"}, exclude_none=True)
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

    # ── Daily Digest Operations ──

    def add_to_digest(self, job_id: str, digest_date: Optional[date] = None) -> bool:
        """Queue a job for the nightly PDF digest. Skips silently on duplicate."""
        target_date = (digest_date or date.today()).isoformat()

        def _add():
            # Check if already in digest for this date (unique constraint will also catch this)
            existing = (
                self.client.table("daily_digest")
                .select("id")
                .eq("job_id", job_id)
                .eq("digest_date", target_date)
                .execute()
            )
            if existing.data:
                logger.debug(f"Job {job_id} already in digest for {target_date}")
                return True

            self.client.table("daily_digest").insert({
                "job_id": job_id,
                "digest_date": target_date,
                "sent": False,
            }).execute()
            return True

        return self._retry(_add) or False

    def get_pending_digest_jobs(self, digest_date: Optional[date] = None) -> List[Job]:
        """Fetch all un-sent digest entries for a date, joined with full job data."""
        target_date = (digest_date or date.today()).isoformat()

        def _fetch():
            # Get digest entries for this date that haven't been sent
            digest_result = (
                self.client.table("daily_digest")
                .select("job_id")
                .eq("digest_date", target_date)
                .eq("sent", False)
                .execute()
            )

            if not digest_result.data:
                return []

            job_ids = [entry["job_id"] for entry in digest_result.data]

            # Fetch full job data for these IDs
            jobs_result = (
                self.client.table("jobs")
                .select("*")
                .in_("id", job_ids)
                .order("scraped_at", desc=True)
                .execute()
            )
            return [Job(**row) for row in jobs_result.data]

        result = self._retry(_fetch)
        return result if result is not None else []

    def get_all_pending_digest_jobs(self) -> List[Job]:
        """Fetch ALL un-sent digest entries across all dates (backlog).
        
        Fallback when today's queue is empty — picks up jobs queued
        on previous days that were never sent.
        """
        def _fetch():
            digest_result = (
                self.client.table("daily_digest")
                .select("job_id")
                .eq("sent", False)
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )

            if not digest_result.data:
                return []

            job_ids = [entry["job_id"] for entry in digest_result.data]

            jobs_result = (
                self.client.table("jobs")
                .select("*")
                .in_("id", job_ids)
                .order("scraped_at", desc=True)
                .execute()
            )
            return [Job(**row) for row in jobs_result.data]

        result = self._retry(_fetch)
        return result if result is not None else []

    def mark_digest_sent(self, digest_date: Optional[date] = None) -> bool:
        """Mark all digest entries for a date as sent."""
        target_date = (digest_date or date.today()).isoformat()

        def _mark():
            self.client.table("daily_digest").update(
                {"sent": True}
            ).eq("digest_date", target_date).eq("sent", False).execute()
            return True

        return self._retry(_mark) or False

    def get_digest_count(self, digest_date: Optional[date] = None) -> int:
        """Get count of pending digest entries for a date."""
        target_date = (digest_date or date.today()).isoformat()

        def _count():
            result = (
                self.client.table("daily_digest")
                .select("id", count="exact")
                .eq("digest_date", target_date)
                .eq("sent", False)
                .limit(1)
                .execute()
            )
            return result.count if result.count is not None else 0

        result = self._retry(_count)
        return result if result is not None else 0

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

    # ── Stats & History ──

    def get_total_jobs_count(self) -> int:
        """Get total number of scraped jobs."""
        def _count():
            result = self.client.table("jobs").select("id", count="exact").limit(1).execute()
            return result.count if result.count is not None else 0
        result = self._retry(_count)
        return result if result is not None else 0

    def get_digests_sent_count(self) -> int:
        """Get total number of digests sent."""
        def _count():
            result = (
                self.client.table("digest_history")
                .select("id", count="exact")
                .limit(1)
                .execute()
            )
            return result.count if result.count is not None else 0
        try:
            result = self._retry(_count)
            return result if result is not None else 0
        except Exception:
            return 0

    def record_digest_history(self, job_count: int, digest_type: str = "scheduled") -> bool:
        """Record a digest send event for history tracking."""
        def _record():
            self.client.table("digest_history").insert({
                "digest_date": date.today().isoformat(),
                "job_count": job_count,
                "digest_type": digest_type,
                "sent": True,
            }).execute()
            return True
        try:
            return self._retry(_record) or False
        except Exception:
            return False

    def get_digest_history(self, limit: int = 30) -> List[dict]:
        """Get recent digest history for dashboard display."""
        def _fetch():
            result = (
                self.client.table("digest_history")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [
                {
                    "date": row.get("digest_date", ""),
                    "job_count": row.get("job_count", 0),
                    "type": row.get("digest_type", "scheduled"),
                    "sent": row.get("sent", False),
                }
                for row in result.data
            ]
        try:
            result = self._retry(_fetch)
            return result if result is not None else []
        except Exception:
            return []

    # ── 15-Day Job Window ──

    def get_jobs_last_n_days(self, days: int = 15) -> List[Job]:
        """Fetch all jobs scraped in the last N days, sorted by most recent first.

        This is the primary data source for the digest email — ensures
        the user always sees a 15-day rolling window of jobs regardless
        of the daily_digest queue state.
        """
        def _fetch():
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            result = (
                self.client.table("jobs")
                .select("*")
                .gte("scraped_at", cutoff)
                .order("scraped_at", desc=True)
                .limit(200)
                .execute()
            )
            return [Job(**row) for row in result.data]

        result = self._retry(_fetch)
        return result if result is not None else []

    # ── Auto-Cleanup (15 days rolling window) ──

    def cleanup_old_data(self, days: int = 15) -> dict:
        """Delete data older than N days (default 15 days) to protect Supabase free storage.

        Deletes:
        - Jobs older than N days (CASCADE removes related sent_alerts,
          exam_reminders, and daily_digest entries automatically)
        - Old digest_history records older than N days

        Returns dict with counts of deleted records.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        stats = {"jobs_deleted": 0, "digest_history_deleted": 0, "errors": []}

        # Delete old jobs (CASCADE handles sent_alerts, exam_reminders, daily_digest)
        try:
            result = (
                self.client.table("jobs")
                .delete()
                .lt("scraped_at", cutoff)
                .execute()
            )
            stats["jobs_deleted"] = len(result.data) if result.data else 0
            logger.info(f"🗑️ Cleaned up {stats['jobs_deleted']} old jobs (>{days} days)")
        except Exception as e:
            stats["errors"].append(f"jobs cleanup: {e}")
            logger.error(f"Jobs cleanup failed: {e}")

        # Delete old digest_history
        try:
            result = (
                self.client.table("digest_history")
                .delete()
                .lt("created_at", cutoff)
                .execute()
            )
            stats["digest_history_deleted"] = len(result.data) if result.data else 0
            logger.info(f"🗑️ Cleaned up {stats['digest_history_deleted']} old digest history records")
        except Exception as e:
            stats["errors"].append(f"digest_history cleanup: {e}")
            logger.error(f"Digest history cleanup failed: {e}")

        return stats

