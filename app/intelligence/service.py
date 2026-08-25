"""Job Intelligence Coordinator Service.

Coordinates Groq Agent #1 (Job Intelligence), Deterministic Match Engine,
and Groq Agent #2 (Reality Research) with caching and Top-N limit controls.
"""
import logging
import hashlib
from datetime import date, datetime
from typing import List, Dict, Optional, Any

from app.config import get_settings
from app.models import Job, Profile
from app.intelligence.models import (
    JobIntelligenceResult, StructuredJobInfo, JobMatchAnalysis, RealityAnalysis
)
from app.intelligence.job_analyzer import JobIntelligenceAgent
from app.intelligence.match_engine import DeterministicMatchEngine
from app.intelligence.reality_researcher import JobRealityResearcher

logger = logging.getLogger(__name__)


class JobIntelligenceService:
    """End-to-end intelligence and reality check orchestrator."""

    _instance = None
    _cache: Dict[str, JobIntelligenceResult] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.settings = get_settings()
        self.analyzer = JobIntelligenceAgent()
        self.matcher = DeterministicMatchEngine()
        self.researcher = JobRealityResearcher()

    def analyze_single_job(self, job: Job, profile: Profile, force_refresh: bool = False) -> JobIntelligenceResult:
        """Run complete intelligence analysis on a single job with caching."""
        cache_key = self._generate_cache_key(job, profile)
        if not force_refresh and cache_key in self._cache:
            logger.info(f"🧠 Intelligence Cache Hit for: {job.title} @ {job.organization}")
            return self._cache[cache_key]

        logger.info(f"🔍 Analyzing Job Intelligence for: {job.title} @ {job.organization}")

        # Check if expired
        is_expired = bool(job.last_date and job.last_date < date.today())

        # Step 1: Agent #1 Extracts Structured Job Info
        structured_info = self.analyzer.analyze_job(job, profile)

        # Step 2: Deterministic 6-Category Match Engine
        match_analysis = self.matcher.evaluate(profile, structured_info, job)

        # Step 3: Agent #2 Researches Reality Check
        reality_analysis = self.researcher.research(structured_info, job)

        # Combine into final result
        result = JobIntelligenceResult(
            job_id=job.id or str(hash(job.raw_hash)),
            title=job.title,
            company=job.organization,
            location=structured_info.location,
            salary=job.salary,
            vacancies=job.vacancies,
            last_date=job.last_date,
            is_expired=is_expired,
            apply_link=job.apply_link,
            notification_link=job.notification_link,
            source_portal=job.source,
            structured_info=structured_info,
            match=match_analysis,
            reality=reality_analysis,
            overall_recommendation=match_analysis.recommendation,
            updated_at=datetime.utcnow()
        )

        self._cache[cache_key] = result
        return result

    def run_intelligence_pipeline(
        self,
        jobs: List[Job],
        profile: Profile,
        limit: Optional[int] = None,
        exclude_expired: bool = True,
        force_refresh: bool = False
    ) -> List[JobIntelligenceResult]:
        """Run intelligence pipeline over candidate jobs, research top N, and rank by score."""
        max_research = limit or self.settings.job_reality_research_limit

        # 1. Filter out expired jobs if requested
        today = date.today()
        active_jobs = [j for j in jobs if not (exclude_expired and j.last_date and j.last_date < today)]

        if not active_jobs and jobs:
            logger.warning("All input jobs were expired; falling back to non-expired subset or all.")
            active_jobs = jobs if not exclude_expired else [j for j in jobs if not (j.last_date and j.last_date < today)]

        results: List[JobIntelligenceResult] = []

        # 2. Select top active candidates for analysis
        candidate_pool = active_jobs[:max(max_research * 2, 8)]
        candidate_matches = []
        import time

        for job in candidate_pool:
            cache_key = self._generate_cache_key(job, profile)
            if not force_refresh and cache_key in self._cache:
                results.append(self._cache[cache_key])
            else:
                struct = self.analyzer.analyze_job(job, profile)
                match_res = self.matcher.evaluate(profile, struct, job)
                candidate_matches.append((match_res.match_score, job, struct, match_res))
                time.sleep(0.15)  # gentle pacing for Groq LPU

        # 3. Sort candidate matches by match score descending
        candidate_matches.sort(key=lambda x: x[0], reverse=True)

        # 4. Deep Reality Research on Top N candidates
        for idx, (score, job, struct, match_res) in enumerate(candidate_matches):
            cache_key = self._generate_cache_key(job, profile)
            if idx < max_research:
                reality = self.researcher.research(struct, job)
                time.sleep(0.15)  # gentle pacing
            else:
                reality = self.researcher._build_heuristic_reality(struct, job)

            is_expired = bool(job.last_date and job.last_date < today)
            res = JobIntelligenceResult(
                job_id=job.id or str(hash(job.raw_hash)),
                title=job.title,
                company=job.organization,
                location=struct.location,
                salary=job.salary,
                vacancies=job.vacancies,
                last_date=job.last_date,
                is_expired=is_expired,
                apply_link=job.apply_link,
                notification_link=job.notification_link,
                source_portal=job.source,
                structured_info=struct,
                match=match_res,
                reality=reality,
                overall_recommendation=match_res.recommendation,
                updated_at=datetime.utcnow()
            )
            self._cache[cache_key] = res
            results.append(res)

        # Final sort: Highest Match Score first, then Highest Reality Score
        results.sort(key=lambda r: (r.match.match_score, r.reality.reality_score), reverse=True)
        return results

    def get_cached_job(self, job_id: str) -> Optional[JobIntelligenceResult]:
        """Look up analyzed job by ID in cache."""
        for res in self._cache.values():
            if res.job_id == job_id:
                return res
        return None

    def invalidate_cache(self, job_id: Optional[str] = None):
        """Clear specific job or entire cache."""
        if job_id:
            keys_to_del = [k for k, v in self._cache.items() if v.job_id == job_id]
            for k in keys_to_del:
                del self._cache[k]
        else:
            self._cache.clear()

    @staticmethod
    def _generate_cache_key(job: Job, profile: Profile) -> str:
        qual = (profile.qualification or "").lower().strip()
        interests = ",".join(sorted(profile.interests or []))
        raw = f"{job.raw_hash}:{job.organization}:{job.title}:{qual}:{interests}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
