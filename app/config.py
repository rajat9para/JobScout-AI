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

    # ── Twilio ──
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str = "whatsapp:+14155238886"
    user_whatsapp_number: str

    # ── Gemini (Google AI) ──
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"  # Free tier: 15 RPM, 1M tokens/day

    # ── App ──
    app_env: str = "production"
    log_level: str = "INFO"
    scrape_interval_minutes: int = 60  # Hourly to stay within free limits
    max_retries: int = 3
    retry_delay_seconds: int = 5

    # ── Feature Flags ──
    enable_exam_reminders: bool = True
    enable_daily_digest: bool = False  # User can toggle
    enable_bulk_mode: bool = False     # User can toggle

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — call this everywhere instead of direct instantiation."""
    return Settings()
