"""Configuration management with validation and defaults."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All environment variables with sensible defaults for free-tier deployment."""

    # ── Supabase ──
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    # ── Brevo (Sendinblue) Email ──
    brevo_api_key: str
    sender_email: str = "jobscout@noreply.com"
    sender_name: str = "JobScout Bot"
    user_email: str  # Recipient email for nightly digest

    # ── Gemini (Google AI) ──
    gemini_api_key: str
    gemini_model: str = "gemini-3.6-flash"  # Confirmed working — gemini-3.6-flash or gemini-3.5-flash

    # ── App ──
    app_env: str = "production"
    log_level: str = "INFO"
    scrape_interval_minutes: int = 60  # Hourly to stay within free limits
    max_retries: int = 3
    retry_delay_seconds: int = 5

    # ── Digest Settings ──
    digest_send_hour: int = 22  # 10 PM IST (server time) — legacy setting, scheduler uses 10AM/6PM now
    digest_timezone: str = "Asia/Kolkata"

    # ── Feature Flags ──
    enable_exam_reminders: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — call this everywhere instead of direct instantiation."""
    return Settings()
