"""Pydantic models for type safety, validation, and serialization."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class OnboardingState(str, Enum):
    """Finite states for the onboarding conversation state machine."""
    WELCOME = "welcome"
    QUALIFICATION = "qualification"
    INTERESTS = "interests"
    EXPERIENCE = "experience"
    CONFIRMATION = "confirmation"
    COMPLETE = "complete"


class AlertMode(str, Enum):
    """How the user wants to receive alerts."""
    INSTANT = "instant"      # Send immediately when found
    DIGEST = "digest"        # Daily summary at 9 AM
    PAUSED = "paused"        # No alerts


class Profile(BaseModel):
    """User profile stored in Supabase."""
    id: Optional[str] = None
    whatsapp_number: str
    qualification: Optional[str] = None
    interests: Optional[List[str]] = None
    experience_level: Optional[str] = None
    resume_url: Optional[str] = None
    resume_parsed_text: Optional[str] = None
    status: str = "active"           # active | paused
    alert_mode: str = AlertMode.INSTANT.value
    onboarding_state: str = OnboardingState.WELCOME.value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("interests", mode="before")
    @classmethod
    def parse_interests(cls, v):
        """Handle PostgreSQL text[] format and string inputs."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Handle PostgreSQL array format: {a,b,c}
            v = v.strip("{}"")
            return [x.strip().strip(""") for x in v.split(",") if x.strip()]
        return v


class Job(BaseModel):
    """Government job posting extracted from sources."""
    id: Optional[str] = None
    source: str
    title: str
    organization: str
    eligibility: Optional[str] = None
    degree_tags: Optional[List[str]] = None
    salary: Optional[str] = None
    vacancies: Optional[str] = None
    exam_required: Optional[str] = None
    last_date: Optional[date] = None
    apply_link: Optional[str] = None
    raw_hash: str
    raw_text: Optional[str] = None
    scraped_at: Optional[datetime] = None

    @field_validator("degree_tags", mode="before")
    @classmethod
    def parse_degree_tags(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip("{}"")
            return [x.strip().strip(""") for x in v.split(",") if x.strip()]
        return v


class Alert(BaseModel):
    """Record of sent job alerts."""
    id: Optional[str] = None
    job_id: str
    sent_at: Optional[datetime] = None


class ExamReminder(BaseModel):
    """Tracks exam reminders sent to user."""
    id: Optional[str] = None
    job_id: str
    reminder_type: str  # "3_days" | "1_day" | "today"
    sent_at: Optional[datetime] = None
