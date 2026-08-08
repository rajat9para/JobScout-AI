"""FastAPI web service — Twilio webhooks, health checks, and API endpoints.

This is the always-on service that receives WhatsApp messages and
handles the entire conversation flow.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from twilio.twiml.messaging_response import MessagingResponse

from app.config import get_settings
from app.database import Database
from app.models import OnboardingState, AlertMode
from app.onboarding import OnboardingFlow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 JobScout v2 starting up...")
    yield
    logger.info("🛑 JobScout v2 shutting down...")


app = FastAPI(
    title="JobScout v2",
    description="Personal Sarkari Naukri Job Alert Bot — Gemini Edition",
    version="2.0.0",
    lifespan=lifespan
)

db = Database()
onboarding = OnboardingFlow()


@app.get("/")
async def root():
    return {"status": "ok", "service": "JobScout v2", "version": "2.0.0"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "JobScout v2",
        "env": get_settings().app_env,
    }


@app.post("/webhook")
async def twilio_webhook(
    Body: str = Form(default=""),
    From: str = Form(...),
    To: str = Form(...),
    MediaUrl0: str = Form(default=None),
    NumMedia: int = Form(default=0),
):
    """Main entry point for all incoming WhatsApp messages."""
    user_phone = From.replace("whatsapp:", "").strip()
    message_body = Body.strip()
    media_url = MediaUrl0 if NumMedia and NumMedia > 0 else None

    logger.info(f"📩 {user_phone}: {message_body[:60]}...")

    # Get or create profile
    profile = db.get_profile_by_whatsapp(user_phone)
    if not profile:
        logger.info(f"👤 New user: {user_phone}")
        profile = db.create_profile(user_phone)

    # Handle global commands first (available at any time)
    reply = handle_global_commands(profile, message_body)

    # If not a command, handle based on onboarding state
    if reply is None:
        if profile.onboarding_state != OnboardingState.COMPLETE.value:
            reply = onboarding.handle_message(profile, message_body, media_url)
        else:
            reply = handle_post_onboarding(profile, message_body)

    # Build TwiML response
    resp = MessagingResponse()
    resp.message(reply)
    return PlainTextResponse(content=str(resp), media_type="application/xml")


def handle_global_commands(profile, message: str) -> str | None:
    """Check for global commands. Returns reply if matched, None otherwise."""
    cmd = message.lower().strip()

    if cmd == "update":
        db.update_profile(profile.whatsapp_number, {"onboarding_state": "welcome"})
        return "🔄 *Updating profile...* Let's start over."

    elif cmd == "pause":
        db.update_profile(profile.whatsapp_number, {"status": "paused", "alert_mode": "paused"})
        return "⏸️ *Alerts paused.*\nSend *RESUME* anytime to start again."

    elif cmd == "resume":
        db.update_profile(profile.whatsapp_number, {"status": "active", "alert_mode": "instant"})
        return "▶️ *Alerts resumed!* You'll receive job alerts again."

    elif cmd == "status":
        return build_status_message(profile)

    elif cmd == "digest":
        db.update_profile(profile.whatsapp_number, {"alert_mode": "digest"})
        return "📋 *Switched to Daily Digest mode.*\nYou'll get one summary message per day at 9 AM instead of instant alerts."

    elif cmd == "instant":
        db.update_profile(profile.whatsapp_number, {"alert_mode": "instant"})
        return "⚡ *Switched to Instant mode.*\nYou'll get alerts immediately when jobs are found."

    elif cmd == "bulk":
        db.update_profile(profile.whatsapp_number, {"alert_mode": "bulk"})
        return "📦 *Bulk mode ON.*\nYou'll see ALL new government jobs, not just matched ones."

    elif cmd == "matched":
        db.update_profile(profile.whatsapp_number, {"alert_mode": "instant"})
        return "🎯 *Matched mode ON.*\nOnly jobs matching your profile will be sent."

    elif cmd in ["help", "start", "hi", "hello", "hey", "hii"]:
        return build_help_message()

    return None


def handle_post_onboarding(profile, message: str) -> str:
    """Handle messages from users who have completed onboarding."""
    cmd = message.lower().strip()

    # Feedback command
    if cmd.startswith("feedback"):
        feedback = message[8:].strip()
        if feedback:
            logger.info(f"Feedback from {profile.whatsapp_number}: {feedback}")
            return "🙏 *Thank you for your feedback!* It helps us improve."
        return "Please type *FEEDBACK* followed by your message."

    # Stats command
    if cmd == "stats":
        recent = db.get_recent_jobs(hours=24)
        return (
            f"📊 *Stats (Last 24h)*\n\n"
            f"🆕 New jobs found: {len(recent)}\n"
            f"📌 Your status: {profile.status.upper()}\n"
            f"🔔 Alert mode: {profile.alert_mode.upper()}\n"
            f"📚 Qualification: {profile.qualification or 'N/A'}"
        )

    # Default response
    return (
        "You're all set! I'll send you job alerts.\n\n"
        "*Commands:* UPDATE | PAUSE | RESUME | STATUS | DIGEST | BULK | STATS | HELP"
    )


def build_status_message(profile) -> str:
    """Build detailed status message."""
    status_emoji = "🟢" if profile.status == "active" else "🔴"
    mode_emoji = {"instant": "⚡", "digest": "📋", "paused": "⏸️", "bulk": "📦"}.get(profile.alert_mode, "⚡")
    interests = ", ".join(profile.interests) if profile.interests else "N/A"

    return (
        f"📊 *Your Status* {status_emoji}\n\n"
        f"📚 *Qualification:* {profile.qualification or 'N/A'}\n"
        f"📋 *Interests:* {interests}\n"
        f"💼 *Experience:* {profile.experience_level or 'N/A'}\n"
        f"🔔 *Alerts:* {profile.status.upper()}\n"
        f"📬 *Mode:* {mode_emoji} {profile.alert_mode.upper()}\n"
        f"📄 *Resume:* {'✅' if profile.resume_url else '❌'}\n\n"
        "Send *UPDATE* to change profile."
    )


def build_help_message() -> str:
    return (
        "👋 *JobScout Help*\n\n"
        "I send you personalized *government job alerts*.\n\n"
        "*Commands:*\n"
        "• *UPDATE* — Change your profile\n"
        "• *PAUSE* — Stop alerts\n"
        "• *RESUME* — Start alerts\n"
        "• *STATUS* — View your profile\n"
        "• *DIGEST* — Daily summary mode\n"
        "• *INSTANT* — Instant alert mode\n"
        "• *BULK* — See ALL jobs (not just matched)\n"
        "• *MATCHED* — Only matched jobs\n"
        "• *STATS* — Today's job stats\n"
        "• *FEEDBACK* <msg> — Send feedback\n"
        "• *HELP* — Show this message"
    )


@app.get("/profile")
async def get_profile():
    """Debug endpoint to view current profile."""
    settings = get_settings()
    profile = db.get_profile_by_whatsapp(settings.user_whatsapp_number)
    if profile:
        return JSONResponse(content=profile.model_dump(mode="json"))
    return JSONResponse(content={"error": "No profile found"}, status_code=404)
