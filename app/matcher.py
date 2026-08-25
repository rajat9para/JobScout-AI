"""Job-to-profile matching with multi-criteria scoring and ranked preference weighting.

Computes a granular 0-100% Match Compatibility Score based on:
1. Qualification & Degree alignment (35%)
2. Ranked Sector Preferences hierarchy (35%)
3. Experience level suitability (15%)
4. Application deadline & direct link presence (15%)
"""
import logging
from typing import List, Optional
from datetime import date
from app.models import Profile, Job

logger = logging.getLogger(__name__)


class JobMatcher:
    """Matches jobs against user profile with ranked preference scoring."""

    FRESHER_KEYWORDS = [
        "fresher", "freshers", "entry level", "entry-level",
        "trainee", "apprentice", "intern", "graduate",
        "no experience", "0 year", "0-1 year", "0-2 year",
        "beginner", "novice", "junior"
    ]

    EXPERIENCE_MAP = {"fresher": 0, "0-2 yrs": 1, "2+ yrs": 2}

    INTEREST_KEYWORDS = {
        "psu": ["psu", "public sector", "bhel", "ntpc", "ongc", "iocl", "gail", "bpcl", "hpcl", "sail", "nlc", "nmdc", "coal india", "power grid", "nhpc", "bharat electronics", "bel", "hal", "drdo", "isro", "bhabha atomic", "npcil", "cil", "iocl"],
        "banking": ["bank", "rbi", "sbi", "ibps", "reserve bank", "nabard", "sidbi", "nhb", "exim bank", "canara", "pnb", "bob", "union bank"],
        "railways": ["railway", "rrb", "rpf", "metro", "rail", "railtel", "ircon", "rvnl", "dmrc", "rites", "dfccil"],
        "defence": ["defence", "defense", "army", "navy", "air force", "drdo", "isro", "bsf", "crpf", "itbp", "ssb", "cds", "nda", "afc", "coast guard", "paramilitary", "mod", "military", "agniveer"],
        "it/software": ["it", "software", "computer", "developer", "programmer", "technical officer", "scientist", "data scientist", "ai", "machine learning", "cyber security", "nic", "cdac", "stqc"],
        "ssc": ["ssc", "staff selection", "cgl", "chsl", "mts", "delhi police", "constable", "cpo", "je"],
        "upsc": ["upsc", "civil service", "ias", "ips", "ifs", "central service", "combined defence", "cds", "nda", "epfo", "capf"],
        "teaching": ["teacher", "professor", "lecturer", "faculty", "education", "tgt", "pgt", "assistant professor", "prt", "kv", "kvs", "nvs", "ctet"],
        "state govt": ["state", "state government", "district", "panchayat", "municipal", "mpsc", "state psc", "uppsc", "bpsc", "rpsc", "wbpsc", "hpsc", "tspsc", "appsc"],
        "judiciary": ["judge", "judicial", "court", "high court", "supreme court", "law officer", "public prosecutor", "legal assistant"],
        "medical": ["doctor", "medical officer", "nurse", "pharmacist", "health", "aiims", "esic", "cghs", "staff nurse", "mbbs", "bds"],
    }

    def match(self, profile: Profile, job: Job) -> bool:
        """Returns True if job meets minimum criteria and has not expired."""
        if profile.status != "active":
            return False

        # Strictly exclude expired jobs
        if job.last_date and job.last_date < date.today():
            logger.debug(f"⏳ EXPIRED ({job.last_date}): {job.title} @ {job.organization}")
            return False

        qual_match = self._match_qualification(profile, job)
        interest_match = self._match_interests(profile, job)
        exp_match = self._match_experience(profile, job)

        checks_passed = sum([qual_match, interest_match, exp_match])

        # Include if interests match (primary preference) OR at least 2 checks pass
        result = interest_match or checks_passed >= 2

        # Assign computed match score to job object
        job.match_score = self.compute_match_percentage(profile, job)

        if result:
            logger.info(f"✅ MATCH ({job.match_score}%): {job.title} @ {job.organization}")
        else:
            logger.debug(f"❌ SKIP: {job.title} @ {job.organization}")
        return result

    def compute_match_percentage(self, profile: Profile, job: Job) -> int:
        """Compute an accurate 0-100% Match Score based on profile preferences."""
        score = 0

        # 1. Qualification & Degree Alignment (Max 35 points)
        qual_pts = 0
        if profile.qualification:
            user_deg = profile.qualification.lower().strip()
            job_degrees = [d.lower() for d in (job.degree_tags or [])]
            eligibility = (job.eligibility or "").lower()

            if any(user_deg == jd for jd in job_degrees):
                qual_pts = 35  # Exact degree match
            elif any(user_deg in jd or jd in user_deg for jd in job_degrees):
                qual_pts = 32  # Substring match
            elif user_deg in eligibility:
                qual_pts = 30  # Found in eligibility text
            elif user_deg in ["b.tech", "b.e.", "be", "b.e"] and any(k in job_degrees + [eligibility] for k in ["b.tech", "b.e.", "engineering", "diploma"]):
                qual_pts = 32  # Engineering equivalence
            elif any(k in job_degrees + [eligibility] for k in ["any graduate", "any branch", "any discipline", "any degree", "graduate"]):
                qual_pts = 24  # General graduate match
            else:
                qual_pts = 10  # Partial match
        else:
            qual_pts = 25
        score += qual_pts

        # 2. Ranked Sector Interest Match (Max 35 points)
        interest_pts = 0
        if profile.interests:
            user_interests = [i.lower().strip() for i in profile.interests]
            job_text = f"{job.title} {job.organization} {job.eligibility or ''} {job.exam_required or ''}".lower()

            if "all" in user_interests:
                interest_pts = 30
            else:
                for rank_idx, interest in enumerate(user_interests):
                    keywords = self.INTEREST_KEYWORDS.get(interest, [interest])
                    if any(kw in job_text for kw in keywords):
                        # Higher score for user's top ranked interests:
                        if rank_idx == 0:
                            interest_pts = 35  # #1 Top Ranked Interest
                        elif rank_idx == 1:
                            interest_pts = 30  # #2 Ranked Interest
                        elif rank_idx == 2:
                            interest_pts = 26  # #3 Ranked Interest
                        else:
                            interest_pts = 22  # Other chosen interests
                        break

                if interest_pts == 0:
                    interest_pts = 8  # Generic govt job bonus
        else:
            interest_pts = 25
        score += interest_pts

        # 3. Experience Match (Max 15 points)
        exp_pts = 0
        if profile.experience_level:
            user_level = self.EXPERIENCE_MAP.get(profile.experience_level.lower(), 0)
            job_text = f"{job.title} {job.eligibility or ''}".lower()
            requires_exp = any(kw in job_text for kw in [
                "2+ years", "3+ years", "5 years", "experience required",
                "experienced candidates only", "minimum 2 years", "senior"
            ])

            if user_level == 0 and not requires_exp:
                exp_pts = 15  # Perfect for fresher
            elif user_level >= 1:
                exp_pts = 15  # Experienced candidate eligible for both
            elif any(kw in job_text for kw in self.FRESHER_KEYWORDS):
                exp_pts = 15
            else:
                exp_pts = 8
        else:
            exp_pts = 12
        score += exp_pts

        # 4. Detail Richness & Deadlines (Max 15 points)
        detail_pts = 0
        if job.last_date:
            days_left = (job.last_date - date.today()).days
            if days_left >= 0:
                detail_pts += 8  # Active deadline
            else:
                detail_pts += 2
        else:
            detail_pts += 4

        if job.apply_link or job.notification_link:
            detail_pts += 7  # Official application link verified

        score += detail_pts

        # Cap between 40% and 99%
        return max(40, min(score, 99))

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
