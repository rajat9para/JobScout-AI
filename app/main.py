"""FastAPI web service — dashboard, APIs, and health checks.

Serves the interactive web dashboard and provides REST API endpoints for:
- Profile management (CRUD, pause/resume)
- Resume upload and AI parsing
- Digest status and history
- Manual triggers for scraping and digest
"""
import logging
import os
import threading
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import Database
from app.dashboard import DASHBOARD_HTML

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

scrape_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 JobScout v2.2 starting up...")
    _ensure_profile_from_env()

    # Start built-in scheduler (scraper + digest + reminders)
    # Only on Render/local — Vercel is serverless, no persistent scheduler
    is_serverless = os.environ.get("VERCEL", "") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "")
    if not is_serverless:
        try:
            from app.scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.warning(f"Scheduler start failed (non-fatal): {e}")

    yield

    # Graceful shutdown
    if not is_serverless:
        try:
            from app.scheduler import stop_scheduler
            stop_scheduler()
        except Exception:
            pass
    logger.info("🛑 JobScout v2.2 shutting down...")


def _ensure_profile_from_env():
    """Log profile status on startup."""
    try:
        settings = get_settings()
        db = Database()
        existing = db.get_profile_by_email(settings.user_email)
        if not existing:
            logger.info(f"📧 No profile for {settings.user_email}. Visit the dashboard to create one.")
        else:
            logger.info(f"📧 Profile: {settings.user_email} | {existing.qualification} | Status: {existing.status}")
    except Exception as e:
        logger.warning(f"Startup profile check failed: {e}")


app = FastAPI(
    title="JobScout v2.2",
    description="Personal Sarkari Naukri Job Alert Bot — Web Dashboard Edition",
    version="2.2.0",
    lifespan=lifespan
)

# Mount static files (logo, etc.)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

db = Database()


# ══════════════════════════════════════════════════════════════
#  DASHBOARD & HEALTH
# ══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the interactive web dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "JobScout v2.2", "env": get_settings().app_env}


# ══════════════════════════════════════════════════════════════
#  PROFILE API
# ══════════════════════════════════════════════════════════════

@app.get("/api/profile")
async def get_profile():
    """Get current user profile."""
    settings = get_settings()
    profile = db.get_profile_by_email(settings.user_email)
    if not profile:
        profile = db.get_first_active_profile()
    if profile:
        return JSONResponse(content=profile.model_dump(mode="json"))
    return JSONResponse(content={"error": "No profile found. Use the dashboard to create one."}, status_code=404)


@app.post("/api/profile")
async def save_profile(request: Request):
    """Create or update user profile."""
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        qualification = data.get("qualification", "").strip()
        interests = data.get("interests", [])
        experience_level = data.get("experience_level", "Fresher").strip()

        if not email or not qualification:
            return JSONResponse(content={"error": "Email and qualification are required."}, status_code=400)
        if not interests:
            return JSONResponse(content={"error": "Select at least one interest."}, status_code=400)

        profile = db.upsert_profile(
            email=email,
            qualification=qualification,
            interests=interests,
            experience_level=experience_level,
        )

        if profile:
            return JSONResponse(content={"status": "ok", "message": "Profile saved successfully"})
        else:
            return JSONResponse(content={"error": "Database error saving profile"}, status_code=500)

    except Exception as e:
        logger.error(f"Profile save error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/status")
async def update_status(request: Request):
    """Pause or resume notifications."""
    try:
        data = await request.json()
        new_status = data.get("status", "active")
        if new_status not in ("active", "paused"):
            return JSONResponse(content={"error": "Status must be 'active' or 'paused'"}, status_code=400)

        settings = get_settings()
        success = db.update_profile(settings.user_email, {"status": new_status})
        if success:
            logger.info(f"📌 Profile status changed to: {new_status}")
            return JSONResponse(content={"status": new_status})
        return JSONResponse(content={"error": "Profile not found"}, status_code=404)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ══════════════════════════════════════════════════════════════
#  RESUME API
# ══════════════════════════════════════════════════════════════

@app.post("/api/resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume, parse with Gemini, update profile."""
    try:
        if file.size and file.size > 5 * 1024 * 1024:
            return JSONResponse(content={"error": "File too large (max 5MB)"}, status_code=400)

        content = await file.read()
        filename = file.filename or "resume.pdf"
        content_type = file.content_type or "application/pdf"

        settings = get_settings()

        # Upload to Supabase Storage
        file_path = f"{settings.user_email}/{filename}"
        resume_url = db.upload_resume(file_path, content, content_type)

        # Extract text (basic for .txt, or store raw for PDFs)
        resume_text = ""
        if filename.lower().endswith(".txt"):
            resume_text = content.decode("utf-8", errors="ignore")[:10000]
        else:
            # For PDF/DOC: store as-is, Gemini can't read binary
            # We'll use the filename and any metadata
            resume_text = f"Resume uploaded: {filename} ({len(content)} bytes)"

        # Parse with Gemini if we have text
        parsed = {}
        if resume_text and len(resume_text) > 50:
            try:
                from app.extractor import JobExtractor
                extractor = JobExtractor()
                parsed = extractor.parse_resume(resume_text)
            except Exception as e:
                logger.warning(f"Resume parsing with Gemini failed: {e}")

        # Update profile with resume data
        updates = {"resume_url": resume_url}
        if resume_text:
            updates["resume_parsed_text"] = resume_text[:5000]
        if parsed.get("qualification"):
            updates["qualification"] = parsed["qualification"]
        if parsed.get("experience_level"):
            updates["experience_level"] = parsed["experience_level"]

        db.update_profile(settings.user_email, updates)

        return JSONResponse(content={
            "status": "ok",
            "message": "Resume uploaded and analyzed",
            "parsed": parsed,
            "url": resume_url,
        })

    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ══════════════════════════════════════════════════════════════
#  STATS & HISTORY API
# ══════════════════════════════════════════════════════════════

@app.get("/api/stats")
async def get_stats():
    """Dashboard statistics."""
    try:
        pending = db.get_digest_count()
        total_jobs = db.get_total_jobs_count()
        digests_sent = db.get_digests_sent_count()
        return {
            "pending_today": pending,
            "total_jobs": total_jobs,
            "digests_sent": digests_sent,
            "sources": 4,
        }
    except Exception as e:
        return {"pending_today": 0, "total_jobs": 0, "digests_sent": 0, "sources": 4}


@app.get("/api/digest-status")
async def digest_status():
    """Check today's pending digest."""
    count = db.get_digest_count()
    return {"date": date.today().isoformat(), "pending_jobs": count, "status": "ready" if count > 0 else "empty"}


@app.get("/api/digest-history")
async def digest_history():
    """Get digest send history."""
    try:
        history = db.get_digest_history(limit=30)
        return JSONResponse(content=history)
    except Exception as e:
        return JSONResponse(content=[], status_code=200)


# ══════════════════════════════════════════════════════════════
#  TRIGGER ACTIONS
# ══════════════════════════════════════════════════════════════

@app.get("/api/trigger-digest")
async def trigger_digest():
    """Manually trigger report email.
    
    Strategy:
    1. First try: pending jobs from today's daily_digest queue
    2. Fallback: pending jobs from ANY date (not yet sent)
    3. Last resort: pull last 15 days of jobs (profile-filtered)
    
    This ensures the button ALWAYS works, even if no scraper has run.
    """
    try:
        from app.pdf_generator import PDFGenerator
        from app.brevo_mailer import BrevoMailer
        from app.matcher import JobMatcher

        settings = get_settings()
        logger.info("📧 Manual report trigger started")

        # Get profile
        profile = db.get_profile_by_email(settings.user_email)
        if not profile:
            profile = db.get_first_active_profile()
        if not profile:
            logger.error("No profile found for digest")
            return JSONResponse(content={"error": "No profile found. Please save your profile first."}, status_code=404)

        user_email = profile.email or settings.user_email
        logger.info(f"📧 Report for: {user_email}")

        # Strategy 1: Today's pending digest queue
        jobs = db.get_pending_digest_jobs()
        source = "queued"
        logger.info(f"📋 Today's digest queue: {len(jobs)} jobs")

        # Strategy 2: Any date's unsent digest entries
        if not jobs:
            jobs = db.get_all_pending_digest_jobs()
            source = "backlog"
            logger.info(f"📋 Backlog digest queue: {len(jobs)} jobs")

        # Strategy 3: Last 15 days of jobs (profile-filtered)
        if not jobs:
            all_recent = db.get_jobs_last_n_days(days=15)
            logger.info(f"📋 15-day window: {len(all_recent)} total jobs")
            if all_recent:
                matcher = JobMatcher()
                jobs = [j for j in all_recent if matcher.match(profile, j)]
                logger.info(f"📋 After profile filter: {len(jobs)} matching jobs")
                if not jobs:
                    jobs = all_recent  # Include all if no matches
            source = "15day_window"

        if not jobs:
            logger.info("No jobs found anywhere for report")
            return {"status": "skipped", "message": "No jobs found. Run a scrape first to populate the database.", "jobs": 0, "email": user_email}

        # Generate PDF
        pdf_gen = PDFGenerator()
        pdf_bytes = pdf_gen.generate(jobs)
        logger.info(f"📄 PDF generated: {len(pdf_bytes)} bytes, {len(jobs)} jobs")

        # Send email
        mailer = BrevoMailer()
        success = mailer.send_digest_email(
            to_email=user_email,
            pdf_bytes=pdf_bytes,
            job_count=len(jobs),
        )

        if success:
            if source in ("queued", "backlog"):
                db.mark_digest_sent()
            db.record_digest_history(len(jobs), "manual")
            logger.info(f"✅ Manual report sent: {len(jobs)} jobs to {user_email} (source: {source})")
            return {"status": "sent", "jobs": len(jobs), "email": user_email, "source": source}
        else:
            error_detail = mailer.last_error or "Email send failed. Check Brevo API key and sender email verification."
            logger.error(f"❌ Brevo send_digest_email returned False: {error_detail}")
            return JSONResponse(content={"error": error_detail}, status_code=500)

    except Exception as e:
        logger.error(f"Manual report trigger failed: {e}", exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/trigger-scrape")
async def trigger_scrape():
    """Manually trigger scraper in background thread."""
    if not scrape_lock.acquire(blocking=False):
        return JSONResponse(content={"error": "A scrape is already in progress. Please wait."}, status_code=429)

    def _run_scraper():
        try:
            from cron.scraper_job import run_scraper_job
            run_scraper_job()
        except Exception as e:
            logger.error(f"Manual scrape error: {e}")
        finally:
            scrape_lock.release()

    thread = threading.Thread(target=_run_scraper, daemon=True)
    thread.start()
    return {"status": "started", "message": "Scraper running in background"}


@app.get("/api/test-email")
async def test_email(email: Optional[str] = None):
    """Send a test email to verify Brevo mail service is working."""
    try:
        settings = get_settings()
        user_email = email or settings.user_email

        if not email:
            profile = db.get_profile_by_email(user_email)
            if profile and profile.email:
                user_email = profile.email

        from app.brevo_mailer import BrevoMailer
        mailer = BrevoMailer()
        success = mailer.send_test_email(to_email=user_email)

        if success:
            return {"status": "sent", "email": user_email, "message": "Test email sent! Check your inbox."}
        else:
            # Return specific error from mailer
            error_detail = mailer.last_error or "Email send failed. Check Brevo API key and sender verification."
            return JSONResponse(content={"error": error_detail}, status_code=500)

    except Exception as e:
        logger.error(f"Test email failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/verify-brevo")
async def verify_brevo():
    """Diagnose Brevo email service — checks API key, IP restrictions, sender verification, and credits."""
    try:
        from app.brevo_mailer import BrevoMailer
        mailer = BrevoMailer()
        result = mailer.verify_connection()
        if result["ok"]:
            return {
                "status": "ok",
                "account": result["account"],
                "plan": result["plan"],
                "credits": result["credits"],
                "sender_verified": result["sender_verified"],
                "sender_email": mailer.sender_email,
                "message": "Brevo email service is fully operational ✅"
            }
        else:
            return JSONResponse(content={
                "status": "error",
                "error": result["error"],
                "sender_email": mailer.sender_email,
            }, status_code=500)
    except Exception as e:
        logger.error(f"Brevo verification failed: {e}")
        return JSONResponse(content={"status": "error", "error": str(e)}, status_code=500)


@app.get("/api/scheduler-status")
async def scheduler_status():
    """Check if built-in scheduler is running and list next run times."""
    try:
        from app.scheduler import scheduler
        if not scheduler.running:
            return {"running": False, "jobs": []}
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else "N/A",
            })
        return {"running": True, "jobs": jobs}
    except Exception as e:
        return {"running": False, "error": str(e)}


@app.get("/api/debug")
async def debug_pipeline():
    """Full pipeline diagnostic — checks every component end-to-end.

    Tests:
    1. Gemini API key + model validity
    2. Supabase connection + table counts
    3. Scheduler status
    4. Last 15 days job count
    5. Today's digest queue count

    Use this to instantly identify which stage is broken.
    """
    result = {
        "timestamp": datetime.now().isoformat(),
        "gemini": {"ok": False, "model": None, "error": None},
        "supabase": {"ok": False, "jobs_total": 0, "jobs_15d": 0, "digest_pending": 0, "error": None},
        "scheduler": {"running": False, "jobs": []},
        "profile": {"found": False, "email": None, "status": None},
        "verdict": "❌ Pipeline broken — see individual checks above",
    }

    settings = get_settings()

    # ── 1. Gemini check ──
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)
        test_resp = model.generate_content(
            "Reply with exactly: OK",
            generation_config=genai.GenerationConfig(max_output_tokens=5, temperature=0)
        )
        result["gemini"]["ok"] = True
        result["gemini"]["model"] = settings.gemini_model
        result["gemini"]["response"] = test_resp.text.strip()
    except Exception as e:
        result["gemini"]["error"] = str(e)
        result["gemini"]["model"] = settings.gemini_model

    # ── 2. Supabase + job counts ──
    try:
        total = db.get_total_jobs_count()
        recent = db.get_jobs_last_n_days(days=15)
        pending = db.get_digest_count()
        result["supabase"]["ok"] = True
        result["supabase"]["jobs_total"] = total
        result["supabase"]["jobs_15d"] = len(recent)
        result["supabase"]["digest_pending"] = pending
    except Exception as e:
        result["supabase"]["error"] = str(e)

    # ── 3. Scheduler check ──
    try:
        from app.scheduler import scheduler
        result["scheduler"]["running"] = scheduler.running
        if scheduler.running:
            result["scheduler"]["jobs"] = [
                {"id": j.id, "name": j.name, "next_run": str(j.next_run_time)}
                for j in scheduler.get_jobs()
            ]
    except Exception as e:
        result["scheduler"]["error"] = str(e)

    # ── 4. Profile check ──
    try:
        profile = db.get_profile_by_email(settings.user_email)
        if not profile:
            profile = db.get_first_active_profile()
        if profile:
            result["profile"]["found"] = True
            result["profile"]["email"] = profile.email
            result["profile"]["status"] = profile.status
            result["profile"]["qualification"] = profile.qualification
            result["profile"]["interests"] = profile.interests
    except Exception as e:
        result["profile"]["error"] = str(e)

    # ── Overall verdict ──
    all_ok = (
        result["gemini"]["ok"]
        and result["supabase"]["ok"]
        and result["profile"]["found"]
    )
    if all_ok and result["supabase"]["jobs_total"] > 0:
        result["verdict"] = f"✅ Pipeline healthy — {result['supabase']['jobs_total']} total jobs, {result['supabase']['jobs_15d']} in last 15 days"
    elif all_ok and result["supabase"]["jobs_total"] == 0:
        result["verdict"] = "⚠️ Pipeline OK but no jobs in DB yet — trigger a scrape first"
    elif not result["gemini"]["ok"]:
        result["verdict"] = f"❌ Gemini API broken — fix GEMINI_MODEL or GEMINI_API_KEY. Error: {result['gemini']['error']}"
    elif not result["supabase"]["ok"]:
        result["verdict"] = f"❌ Supabase broken — check SUPABASE_URL / SUPABASE_SERVICE_KEY"
    elif not result["profile"]["found"]:
        result["verdict"] = "❌ No profile found — visit dashboard and save your profile first"

    return JSONResponse(content=result)


