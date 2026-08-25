"""Pydantic data models for the AI Job Intelligence & Reality Check subsystem."""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SalaryInfo(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    currency: str = "INR"
    raw_text: Optional[str] = None


class StructuredJobInfo(BaseModel):
    """Normalized structured data extracted by Groq Agent #1."""
    job_title: str
    company: str
    location: str = "India"
    work_mode: str = "On-site"  # On-site, Hybrid, Remote
    experience_required: str = "Fresher / 0-2 yrs"
    seniority: str = "Entry / Mid"
    salary: Optional[SalaryInfo] = None
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    job_type: str = "Full-time"
    application_fee: Optional[str] = None
    selection_process: Optional[str] = None
    last_date: Optional[date] = None


class CategoryScores(BaseModel):
    skill_match: int = 0         # Weight: 35%
    experience_match: int = 0    # Weight: 20%
    role_match: int = 0          # Weight: 20%
    location_match: int = 0      # Weight: 10%
    salary_match: int = 0        # Weight: 10%
    work_mode_match: int = 0     # Weight: 5%


class JobMatchAnalysis(BaseModel):
    """Deterministic profile match analysis."""
    match_score: int = 0  # 0-100%
    category_scores: CategoryScores = Field(default_factory=CategoryScores)
    matched_requirements: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    missing_nice_to_have: List[str] = Field(default_factory=list)
    potential_risks: List[str] = Field(default_factory=list)
    recommendation: str = "APPLY"  # STRONG APPLY | APPLY | INVESTIGATE | CONSIDER | SKIP
    match_summary: str = ""


class EvidenceClaim(BaseModel):
    """An evidence-based factual theme gathered from public signals."""
    claim: str
    source_count: int = 1
    positive_mentions: int = 0
    negative_mentions: int = 0
    neutral_mentions: int = 0
    recency: str = "recent"
    confidence: str = "medium"  # high | medium | low | insufficient


class SourceCitation(BaseModel):
    """Transparent source reference for employee/interview signals."""
    source_name: str
    url: Optional[str] = None
    recency: Optional[str] = None
    snippet: Optional[str] = None
    confidence: str = "medium"


class InterviewIntelligence(BaseModel):
    """Observed interview rounds, technical topics, and difficulty."""
    rounds_count: Optional[str] = "2-3 Rounds"
    technical_difficulty: float = 3.5  # 1-5 scale
    common_topics: List[str] = Field(default_factory=list)
    system_design_expectations: Optional[str] = None
    behavioral_themes: Optional[str] = None
    candidate_tips: Optional[str] = None


class RealityAnalysis(BaseModel):
    """Workplace reality, culture, and employee signals from Groq Agent #2."""
    reality_score: int = 75  # 0-100
    confidence: str = "Medium"  # High | Medium | Low | Insufficient Public Evidence
    employee_sentiment: float = 3.8    # 1-5 scale
    work_life_balance: float = 3.5     # 1-5 scale
    learning_growth: float = 4.0       # 1-5 scale
    management_culture: float = 3.6    # 1-5 scale
    interview_difficulty: float = 3.5  # 1-5 scale
    positive_signals: List[str] = Field(default_factory=list)
    potential_concerns: List[str] = Field(default_factory=list)
    common_themes: List[str] = Field(default_factory=list)
    evidence_claims: List[EvidenceClaim] = Field(default_factory=list)
    interview: Optional[InterviewIntelligence] = None
    sources: List[SourceCitation] = Field(default_factory=list)
    reality_summary: str = ""


class JobIntelligenceResult(BaseModel):
    """Combined end-to-end intelligence record for a single job."""
    job_id: str
    title: str
    company: str
    location: Optional[str] = None
    salary: Optional[str] = None
    vacancies: Optional[str] = None
    last_date: Optional[date] = None
    is_expired: bool = False
    apply_link: Optional[str] = None
    notification_link: Optional[str] = None
    source_portal: str = ""
    structured_info: StructuredJobInfo
    match: JobMatchAnalysis
    reality: RealityAnalysis
    overall_recommendation: str = "APPLY"  # STRONG APPLY | APPLY | INVESTIGATE | CONSIDER | SKIP
    updated_at: datetime = Field(default_factory=datetime.utcnow)
