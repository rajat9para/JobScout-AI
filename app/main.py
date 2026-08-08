"""FastAPI web service — profile setup, health checks, and API endpoints.

This is the always-on service that provides a web form for profile setup,
health checks for UptimeRobot, and debug/trigger endpoints.
"""
import logging
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, HTMLResponse

from app.config import get_settings
from app.database import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 JobScout v2 starting up...")
    # Auto-create profile from env vars if it doesn't exist
    _ensure_profile_from_env()
    yield
    logger.info("🛑 JobScout v2 shutting down...")


def _ensure_profile_from_env():
    """Create a profile from environment variables if one doesn't exist."""
    try:
        settings = get_settings()
        db = Database()
        existing = db.get_profile_by_email(settings.user_email)
        if not existing:
            logger.info(f"📧 No profile for {settings.user_email}. "
                        f"Visit /setup to create your profile.")
        else:
            logger.info(f"📧 Profile found for {settings.user_email}: "
                        f"{existing.qualification} | {existing.interests}")
    except Exception as e:
        logger.warning(f"Could not check profile on startup: {e}")


app = FastAPI(
    title="JobScout v2",
    description="Personal Sarkari Naukri Job Alert Bot — Email Digest Edition",
    version="2.1.0",
    lifespan=lifespan
)

db = Database()


# ── Health & Root ──

@app.get("/")
async def root():
    return {"status": "ok", "service": "JobScout v2", "version": "2.1.0"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "JobScout v2",
        "env": get_settings().app_env,
    }


# ── Profile Setup (Web Form) ──

INTEREST_OPTIONS = [
    "PSU", "Banking", "Railways", "Defence", "IT/Software",
    "SSC", "UPSC", "Teaching", "State Govt", "Judiciary", "Medical"
]

EXPERIENCE_OPTIONS = ["Fresher", "0-2 yrs", "2+ yrs"]


@app.get("/setup", response_class=HTMLResponse)
async def setup_form():
    """Serve the profile setup HTML form."""
    settings = get_settings()

    # Check if profile exists
    existing = db.get_profile_by_email(settings.user_email)
    existing_msg = ""
    if existing:
        interests_str = ", ".join(existing.interests) if existing.interests else "None"
        existing_msg = f"""
        <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 16px; border-radius: 8px; margin-bottom: 24px;">
            <strong>✅ Existing Profile Found</strong><br>
            <span style="color: #555;">Email: {existing.email} | Qualification: {existing.qualification} | 
            Interests: {interests_str} | Experience: {existing.experience_level} | Status: {existing.status}</span><br>
            <small style="color: #777;">Submitting the form below will update your profile.</small>
        </div>
        """

    # Build interest checkboxes
    interest_checkboxes = ""
    for i, opt in enumerate(INTEREST_OPTIONS):
        emoji = ["🏭", "🏦", "🚂", "🎖️", "💻", "📊", "🏛️", "📚", "🏘️", "⚖️", "🏥"][i]
        checked = ""
        if existing and existing.interests and opt.lower() in [x.lower() for x in existing.interests]:
            checked = "checked"
        interest_checkboxes += f"""
        <label style="display: inline-block; margin: 6px 10px; padding: 8px 14px; 
               background: #f0f0f0; border-radius: 20px; cursor: pointer; font-size: 14px;
               transition: background 0.2s;">
            <input type="checkbox" name="interests" value="{opt}" {checked}
                   style="margin-right: 6px;"> {emoji} {opt}
        </label>
        """

    # Build experience radio buttons
    experience_radios = ""
    for opt in EXPERIENCE_OPTIONS:
        checked = ""
        if existing and existing.experience_level and opt.lower() == existing.experience_level.lower():
            checked = "checked"
        experience_radios += f"""
        <label style="display: block; margin: 8px 0; padding: 10px 14px; 
               background: #f0f0f0; border-radius: 8px; cursor: pointer;">
            <input type="radio" name="experience" value="{opt}" {checked}
                   style="margin-right: 8px;"> {opt}
        </label>
        """

    qualification_val = existing.qualification if existing and existing.qualification else ""

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JobScout — Profile Setup</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ 
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 40px 20px;
            }}
            .container {{ 
                max-width: 600px; margin: 0 auto; 
                background: white; border-radius: 16px; 
                padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            }}
            h1 {{ color: #1a73e8; text-align: center; margin-bottom: 8px; font-size: 28px; }}
            .subtitle {{ color: #666; text-align: center; margin-bottom: 30px; font-size: 14px; }}
            .field {{ margin-bottom: 24px; }}
            .field label {{ display: block; font-weight: 600; margin-bottom: 8px; color: #333; font-size: 15px; }}
            input[type="text"], input[type="email"] {{ 
                width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; 
                border-radius: 8px; font-size: 15px; outline: none;
                transition: border-color 0.2s;
            }}
            input[type="text"]:focus, input[type="email"]:focus {{ border-color: #1a73e8; }}
            .btn {{ 
                display: block; width: 100%; padding: 14px; 
                background: #1a73e8; color: white; border: none; 
                border-radius: 8px; font-size: 16px; font-weight: 600; 
                cursor: pointer; transition: background 0.2s;
                margin-top: 10px;
            }}
            .btn:hover {{ background: #1557b0; }}
            .section-title {{ font-size: 13px; color: #888; text-transform: uppercase; 
                             letter-spacing: 1px; margin-bottom: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📋 JobScout Setup</h1>
            <p class="subtitle">Configure your profile to receive nightly job digests via email</p>
            
            {existing_msg}

            <form action="/setup" method="post">
                <div class="field">
                    <label>📧 Email Address</label>
                    <input type="email" name="email" value="{settings.user_email}" 
                           placeholder="your@email.com" required>
                </div>

                <div class="field">
                    <label>📚 Qualification</label>
                    <input type="text" name="qualification" value="{qualification_val}"
                           placeholder="e.g., B.Tech, BSc, BCA, Law, MBA" required>
                </div>

                <div class="field">
                    <label class="section-title">📋 Interests (Select sectors)</label>
                    <div>{interest_checkboxes}</div>
                </div>

                <div class="field">
                    <label class="section-title">💼 Experience Level</label>
                    {experience_radios}
                </div>

                <button type="submit" class="btn">💾 Save Profile &amp; Start Receiving Digests</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.post("/setup")
async def setup_profile(
    email: str = Form(...),
    qualification: str = Form(...),
    interests: list = Form(default=[]),
    experience: str = Form(default="Fresher"),
):
    """Handle profile setup form submission."""
    email = email.strip().lower()
    qualification = qualification.strip()
    experience = experience.strip()

    if not email or not qualification:
        return HTMLResponse(
            content="<h2>Error: Email and Qualification are required.</h2><a href='/setup'>Go back</a>",
            status_code=400
        )

    # Filter valid interests
    valid_interests = [i for i in interests if i in INTEREST_OPTIONS]
    if not valid_interests:
        valid_interests = INTEREST_OPTIONS  # Default to all if none selected

    profile = db.upsert_profile(
        email=email,
        qualification=qualification,
        interests=valid_interests,
        experience_level=experience,
    )

    if profile:
        interests_str = ", ".join(valid_interests)
        html = f"""
        <!DOCTYPE html>
        <html><head><meta charset="UTF-8"><title>Profile Saved</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f0f7ff; 
                   display: flex; align-items: center; justify-content: center; min-height: 100vh; }}
            .card {{ background: white; border-radius: 16px; padding: 40px; max-width: 500px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }}
            h1 {{ color: #0d652d; margin-bottom: 20px; }}
            .detail {{ text-align: left; background: #f8f9fa; border-radius: 8px; 
                      padding: 16px; margin: 20px 0; font-size: 14px; line-height: 1.8; }}
            a {{ color: #1a73e8; text-decoration: none; font-weight: 600; }}
        </style></head>
        <body><div class="card">
            <h1>✅ Profile Saved!</h1>
            <p>You'll receive a nightly PDF digest at <b>10 PM IST</b> with matched government jobs.</p>
            <div class="detail">
                <b>📧 Email:</b> {email}<br>
                <b>📚 Qualification:</b> {qualification}<br>
                <b>📋 Interests:</b> {interests_str}<br>
                <b>💼 Experience:</b> {experience}
            </div>
            <a href="/setup">✏️ Edit Profile</a> &nbsp;|&nbsp; <a href="/profile">📊 View Profile JSON</a>
        </div></body></html>
        """
        return HTMLResponse(content=html)
    else:
        return HTMLResponse(
            content="<h2>❌ Error saving profile. Check logs.</h2><a href='/setup'>Try again</a>",
            status_code=500
        )


# ── Debug Endpoints ──

@app.get("/profile")
async def get_profile():
    """Debug endpoint to view current profile."""
    settings = get_settings()
    profile = db.get_profile_by_email(settings.user_email)
    if profile:
        return JSONResponse(content=profile.model_dump(mode="json"))
    return JSONResponse(content={"error": "No profile found"}, status_code=404)


@app.get("/digest-status")
async def digest_status():
    """Check how many jobs are queued for tonight's digest."""
    count = db.get_digest_count()
    return {
        "date": date.today().isoformat(),
        "pending_jobs": count,
        "status": "ready" if count > 0 else "empty",
    }


@app.get("/trigger-digest")
async def trigger_digest():
    """Manually trigger the nightly digest (for testing/debugging)."""
    try:
        from app.pdf_generator import PDFGenerator
        from app.brevo_mailer import BrevoMailer

        settings = get_settings()
        profile = db.get_profile_by_email(settings.user_email)

        if not profile:
            return JSONResponse(
                content={"error": "No profile found. Visit /setup first."},
                status_code=404
            )

        jobs = db.get_pending_digest_jobs()
        pdf_gen = PDFGenerator()
        pdf_bytes = pdf_gen.generate(jobs)

        mailer = BrevoMailer()
        success = mailer.send_digest_email(
            to_email=settings.user_email,
            pdf_bytes=pdf_bytes,
            job_count=len(jobs),
        )

        if success:
            db.mark_digest_sent()
            return {"status": "sent", "jobs": len(jobs), "email": settings.user_email}
        else:
            return JSONResponse(
                content={"error": "Email send failed. Check Brevo API key and logs."},
                status_code=500
            )

    except Exception as e:
        logger.error(f"Manual digest trigger failed: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
