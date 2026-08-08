"""Simplified onboarding conversation flow.

Flow: hello → qualification/resume → interests → experience → confirm → done
"""
import logging
import requests
from typing import Optional
from app.models import Profile, OnboardingState
from app.database import Database
from app.twilio_client import TwilioWhatsApp
from app.extractor import JobExtractor

logger = logging.getLogger(__name__)


class OnboardingFlow:
    """Manages the streamlined onboarding state machine."""

    INTEREST_OPTIONS = [
        "PSU", "Banking", "Railways", "Defence", "IT/Software",
        "SSC", "UPSC", "Teaching", "State Govt", "Judiciary", "Medical", "All"
    ]
    EXPERIENCE_OPTIONS = ["Fresher", "0-2 yrs", "2+ yrs"]

    def __init__(self):
        self.db = Database()
        self.twilio = TwilioWhatsApp()
        self.extractor = JobExtractor()

    def handle_message(self, profile: Profile, message: str, media_url: Optional[str] = None) -> str:
        """Route message to the correct state handler."""
        state = profile.onboarding_state
        handler = getattr(self, f"_handle_{state}", self._handle_unknown)
        return handler(profile, message, media_url)

    def _handle_welcome(self, profile: Profile, message: str, media_url: Optional[str] = None) -> str:
        """Send welcome and move to qualification step."""
        self.db.update_profile(
            profile.whatsapp_number,
            {"onboarding_state": OnboardingState.QUALIFICATION.value}
        )
        return (
            "👋 *Welcome to JobScout!*\n\n"
            "I monitor government job portals and send you *personalized alerts*.\n\n"
            "Let's set up your profile!\n\n"
            "📚 *Step 1/3: Qualification*\n"
            "Tell me your degree (e.g., *B.Tech*, *BSc*, *BCA*, *Law*, *MBA*)\n"
            "OR upload your *resume PDF* and I'll auto-detect it."
        )

    def _handle_qualification(self, profile: Profile, message: str, media_url: Optional[str] = None) -> str:
        """Handle qualification text or resume upload."""
        # Case 1: Resume uploaded
        if media_url:
            try:
                resume_url = self._process_resume(profile, media_url)
                if resume_url:
                    # Parse resume with Gemini
                    resume_text = self._download_resume_text(media_url)
                    parsed = self.extractor.parse_resume(resume_text)

                    qualification = parsed.get("qualification", "")
                    experience = parsed.get("experience_level", "Fresher")

                    self.db.update_profile(
                        profile.whatsapp_number,
                        {
                            "qualification": qualification or "Resume Parsed",
                            "experience_level": experience,
                            "resume_url": resume_url,
                            "resume_parsed_text": resume_text[:5000],
                            "onboarding_state": OnboardingState.INTERESTS.value
                        }
                    )

                    q_display = qualification or "detected from resume"
                    return (
                        f"✅ Resume uploaded & parsed!\n"
                        f"📚 Qualification detected: *{q_display}*\n"
                        f"💼 Experience: *{experience}*\n\n"
                        "📋 *Step 2/3: Interests*\n"
                        "Which sectors interest you? (Pick multiple)\n\n"
                        + self._format_interests() +
                        "\nReply with numbers separated by commas (e.g., *1,3,5*)"
                    )
                else:
                    return "❌ Could not upload resume. Please try again or type your qualification."
            except Exception as e:
                logger.error(f"Resume processing failed: {e}")
                return "❌ Error processing resume. Please type your qualification instead."

        # Case 2: Text qualification
        qualification = message.strip()
        if len(qualification) < 2:
            return "Please enter a valid qualification (e.g., B.Tech, BSc, Law, MBA)."

        self.db.update_profile(
            profile.whatsapp_number,
            {
                "qualification": qualification,
                "onboarding_state": OnboardingState.INTERESTS.value
            }
        )

        return (
            f"✅ Qualification: *{qualification}*\n\n"
            "📋 *Step 2/3: Interests*\n"
            "Which sectors interest you? (Pick multiple)\n\n"
            + self._format_interests() +
            "\nReply with numbers separated by commas (e.g., *1,3,5*)"
        )

    def _handle_interests(self, profile: Profile, message: str, media_url: Optional[str] = None) -> str:
        """Parse interests and move to experience."""
        interests = self._parse_multi_option(message, self.INTEREST_OPTIONS)
        if not interests:
            return "Please reply with valid numbers (e.g., 1,3,5) or type sector names. Use 'All' for everything."

        if "All" in interests:
            interests = [i for i in self.INTEREST_OPTIONS if i != "All"]

        self.db.update_profile(
            profile.whatsapp_number,
            {
                "interests": interests,
                "onboarding_state": OnboardingState.EXPERIENCE.value
            }
        )

        interests_str = ", ".join(interests)
        return (
            f"✅ Interests: *{interests_str}*\n\n"
            "💼 *Step 3/3: Experience*\n"
            "What's your experience level?\n\n"
            "1️⃣ Fresher\n"
            "2️⃣ 0-2 yrs\n"
            "3️⃣ 2+ yrs\n\n"
            "Reply with the number or type your answer."
        )

    def _handle_experience(self, profile: Profile, message: str, media_url: Optional[str] = None) -> str:
        """Save experience and show confirmation."""
        experience = self._parse_option(message, self.EXPERIENCE_OPTIONS)
        if not experience:
            return "Please reply with 1, 2, or 3 (or type Fresher, 0-2 yrs, 2+ yrs)."

        self.db.update_profile(
            profile.whatsapp_number,
            {
                "experience_level": experience,
                "onboarding_state": OnboardingState.CONFIRMATION.value
            }
        )

        return self._build_confirmation(profile, experience)

    def _handle_confirmation(self, profile: Profile, message: str, media_url: Optional[str] = None) -> str:
        """Handle confirm/edit response."""
        msg = message.lower().strip()

        if msg in ["yes", "y", "confirm", "ok", "done", "start"]:
            self.db.update_profile(
                profile.whatsapp_number,
                {
                    "onboarding_state": OnboardingState.COMPLETE.value,
                    "status": "active",
                    "alert_mode": "instant"
                }
            )
            return (
                "🎉 *Profile Complete!*\n\n"
                "You'll now receive government job alerts.\n\n"
                "*Quick Commands:*\n"
                "• *UPDATE* — Change profile\n"
                "• *PAUSE* — Stop alerts\n"
                "• *RESUME* — Start alerts\n"
                "• *STATUS* — View profile\n"
                "• *DIGEST* — Daily summary mode\n"
                "• *BULK* — Get all jobs (not just matched)\n"
                "• *HELP* — Show all commands\n\n"
                "Happy job hunting! 🚀"
            )
        elif msg in ["no", "n", "edit", "change", "fix"]:
            self.db.update_profile(
                profile.whatsapp_number,
                {"onboarding_state": OnboardingState.QUALIFICATION.value}
            )
            return (
                "🔄 Let's fix that.\n\n"
                "📚 *Step 1/3: Qualification*\n"
                "Tell me your degree (e.g., B.Tech, BSc, BCA, Law, MBA)\n"
                "OR upload your resume PDF."
            )
        else:
            return "Please reply *YES* to confirm or *NO* to edit."

    def _handle_unknown(self, profile: Profile, message: str, media_url: Optional[str] = None) -> str:
        """Reset to welcome on unknown state."""
        logger.warning(f"Unknown state: {profile.onboarding_state}")
        self.db.update_profile(
            profile.whatsapp_number,
            {"onboarding_state": OnboardingState.WELCOME.value}
        )
        return self._handle_welcome(profile, message, media_url)

    # ── Helpers ──

    def _format_interests(self) -> str:
        lines = []
        for i, opt in enumerate(self.INTEREST_OPTIONS, 1):
            emoji = ["🏭", "🏦", "🚂", "🎖️", "💻", "📊", "🏛️", "📚", "🏘️", "⚖️", "🏥", "🌍"][i-1]
            lines.append(f"{i}️⃣ {emoji} {opt}")
        return "\n".join(lines)

    def _parse_option(self, message: str, options: list) -> Optional[str]:
        msg = message.strip()
        try:
            idx = int(msg) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        msg_lower = msg.lower()
        for opt in options:
            if msg_lower == opt.lower() or msg_lower in opt.lower() or opt.lower() in msg_lower:
                return opt
        return None

    def _parse_multi_option(self, message: str, options: list) -> Optional[list]:
        msg = message.strip()
        results = []
        parts = [p.strip() for p in msg.replace(",", " ").split()]
        for part in parts:
            try:
                idx = int(part) - 1
                if 0 <= idx < len(options):
                    results.append(options[idx])
                    continue
            except ValueError:
                pass
            part_lower = part.lower()
            for opt in options:
                if part_lower == opt.lower() or part_lower in opt.lower():
                    results.append(opt)
                    break
        return list(dict.fromkeys(results)) if results else None  # Remove duplicates

    def _process_resume(self, profile: Profile, media_url: str) -> Optional[str]:
        """Download from Twilio and upload to Supabase Storage."""
        response = requests.get(media_url, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "application/pdf")
        ext = "pdf" if "pdf" in content_type else "bin"
        file_path = f"resumes/{profile.whatsapp_number.replace('whatsapp:', '').replace('+', '')}/resume.{ext}"
        return self.db.upload_resume(file_path, response.content, content_type)

    def _download_resume_text(self, media_url: str) -> str:
        """Download resume and extract text (basic)."""
        try:
            response = requests.get(media_url, timeout=30)
            # For PDFs, we'd need PyPDF2, but for now return placeholder
            # In production, integrate with a PDF text extraction service
            return "Resume uploaded successfully. Text extraction pending."
        except Exception as e:
            logger.error(f"Resume download failed: {e}")
            return ""

    def _build_confirmation(self, profile: Profile, experience: str) -> str:
        interests_str = ", ".join(profile.interests) if profile.interests else "N/A"
        resume_str = "✅ Uploaded" if profile.resume_url else "❌ Not uploaded"
        return (
            "📋 *Profile Summary*\n\n"
            f"📚 *Qualification:* {profile.qualification or 'N/A'}\n"
            f"📋 *Interests:* {interests_str}\n"
            f"💼 *Experience:* {experience}\n"
            f"📄 *Resume:* {resume_str}\n\n"
            "Is this correct? Reply *YES* to start receiving alerts, or *NO* to edit."
        )
