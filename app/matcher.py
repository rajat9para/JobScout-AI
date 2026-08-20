"""Job-to-profile matching with scoring and filtering.

v2 uses keyword-based matching with relevance scoring.
Designed to be simple, fast, and easily tunable.
"""
import logging
from typing import List
from app.models import Profile, Job

logger = logging.getLogger(__name__)


class JobMatcher:
    """Matches jobs against user profile with scoring."""

    FRESHER_KEYWORDS = [
        "fresher", "freshers", "entry level", "entry-level",
        "trainee", "apprentice", "intern", "graduate",
        "no experience", "0 year", "0-1 year", "0-2 year",
        "beginner", "novice", "junior"
    ]

    EXPERIENCE_MAP = {"fresher": 0, "0-2 yrs": 1, "2+ yrs": 2}

    INTEREST_KEYWORDS = {
        "psu": ["psu", "public sector", "bhel", "ntpc", "ongc", "iocl", "gail", "bpcl", "hpcl", "sail", "nlc", "nmdc", "coal india", "power grid", "nhpc", "bharat electronics", "bel", "hal", "drdo", "isro", "bhabha atomic"],
        "banking": ["bank", "rbi", "sbi", "ibps", "reserve bank", "nabard", "sidbi", "nhb", "exim bank"],
        "railways": ["railway", "rrb", "rpf", "metro", "rail", "railtel", "ircon", "rvnl"],
        "defence": ["defence", "defense", "army", "navy", "air force", "drdo", "isro", "bsf", "crpf", "itbp", "ssb", "cds", "nda", "afc", "coast guard", "paramilitary"],
        "it/software": ["it", "software", "computer", "developer", "programmer", "technical officer", "scientist", "data scientist", "ai", "machine learning", "cyber security"],
        "ssc": ["ssc", "staff selection", "cgl", "chsl", "mtc", "delhi police", "constable"],
        "upsc": ["upsc", "civil service", "ias", "ips", "ifs", "central service", "combined defence", "cds"],
        "teaching": ["teacher", "professor", "lecturer", "faculty", "education", "tgt", "pgt", "assistant professor"],
        "state govt": ["state", "state government", "district", "panchayat", "municipal", "mpsc", "state psc"],
        "judiciary": ["judge", "judicial", "court", "high court", "supreme court", "law officer", "public prosecutor"],
        "medical": ["doctor", "medical officer", "nurse", "pharmacist", "health", "aiims", "esic", "cghs"],
    }

    def match(self, profile: Profile, job: Job) -> bool:
        """Returns True if job matches profile.

        Uses relaxed 2-of-3 scoring: if at least 2 checks pass OR
        interests match, the job is included. This prevents good jobs
        from being filtered out when Gemini fails to extract perfect data.
        """
        if profile.status != "active":
            return False

        qual_match = self._match_qualification(profile, job)
        interest_match = self._match_interests(profile, job)
        exp_match = self._match_experience(profile, job)

        checks_passed = sum([qual_match, interest_match, exp_match])

        # Include if: interests match (primary filter) OR at least 2/3 checks pass
        result = interest_match or checks_passed >= 2

        if result:
            logger.info(f"✅ MATCH: {job.title} @ {job.organization} "
                        f"(qual={qual_match}, interest={interest_match}, exp={exp_match})")
        else:
            logger.debug(f"❌ SKIP: {job.title} @ {job.organization} "
                         f"(qual={qual_match}, interest={interest_match}, exp={exp_match})")
        return result

    def _match_qualification(self, profile: Profile, job: Job) -> bool:
        """Check if job's required degrees match user's qualification."""
        if not profile.qualification:
            return True

        user_deg = profile.qualification.lower().strip()
        job_degrees = [d.lower() for d in (job.degree_tags or [])]
        eligibility = (job.eligibility or "").lower()

        # Direct match
        if any(user_deg in jd or jd in user_deg for jd in job_degrees):
            return True
        if user_deg in eligibility:
            return True

        # B.Tech ↔ B.E. equivalence
        if user_deg in ["b.tech", "b.e.", "be", "b.e"]:
            if any(k in job_degrees + [eligibility] for k in ["b.tech", "b.e.", "be", "b.e", "engineering"]):
                return True

        # BSc/BCA/MCA equivalence for IT roles
        if user_deg in ["bsc", "bca", "mca"]:
            if "it" in eligibility or "computer" in eligibility or "software" in eligibility:
                return True

        # Law degree matching
        if "law" in user_deg or "llb" in user_deg or "llm" in user_deg:
            if any(k in job_degrees + [eligibility] for k in ["law", "llb", "llm", "legal"]):
                return True

        # Any Graduate catch-all
        if any(k in job_degrees + [eligibility] for k in ["any graduate", "any branch", "any discipline", "any degree"]):
            return True

        return False

    def _match_interests(self, profile: Profile, job: Job) -> bool:
        """Check if job sector matches user's interests."""
        if not profile.interests:
            return True

        user_interests = [i.lower().strip() for i in profile.interests]
        if "all" in user_interests:
            return True

        job_text = f"{job.title} {job.organization} {job.eligibility or ''} {job.exam_required or ''}".lower()

        for interest in user_interests:
            keywords = self.INTEREST_KEYWORDS.get(interest, [interest])
            if any(kw in job_text for kw in keywords):
                return True

        return False

    def _match_experience(self, profile: Profile, job: Job) -> bool:
        """Check experience compatibility."""
        if not profile.experience_level:
            return True

        user_level = self.EXPERIENCE_MAP.get(profile.experience_level.lower(), 0)
        job_text = f"{job.title} {job.eligibility or ''}".lower()

        requires_exp = any(kw in job_text for kw in [
            "2+ years", "3+ years", "5 years", "experience required",
            "experienced candidates only", "minimum 2 years", "senior"
        ])

        if user_level == 0 and not requires_exp:
            return True
        if user_level >= 1:
            return True

        is_fresher_friendly = any(kw in job_text for kw in self.FRESHER_KEYWORDS)
        if is_fresher_friendly:
            return True

        return False

    def score_match(self, profile: Profile, job: Job) -> float:
        """Relevance score 0.0–1.0 for ranking."""
        score = 0.0
        if self._match_qualification(profile, job): score += 0.4
        if self._match_interests(profile, job): score += 0.4
        if self._match_experience(profile, job): score += 0.2
        return score
