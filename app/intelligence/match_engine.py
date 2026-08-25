"""Deterministic 6-Category Job Match Engine.

Computes explainable, transparent candidate-to-job compatibility scores based on:
1. Skill & Qualification Alignment (35%)
2. Experience Level Match (20%)
3. Role & Sector Preference Alignment (20%)
4. Location Compatibility (10%)
5. Salary & Compensation Satisfaction (10%)
6. Work Mode Compatibility (5%)
"""
import re
from datetime import date
from typing import Optional, List, Dict, Tuple
from app.intelligence.models import (
    StructuredJobInfo, JobMatchAnalysis, CategoryScores
)
from app.models import Profile, Job


class DeterministicMatchEngine:
    """Calculates deterministic weighted scores with explainable category breakdowns."""

    WEIGHTS = {
        "skill": 0.35,
        "experience": 0.20,
        "role": 0.20,
        "location": 0.10,
        "salary": 0.10,
        "work_mode": 0.05,
    }

    def evaluate(self, profile: Profile, job_info: StructuredJobInfo, raw_job: Optional[Job] = None) -> JobMatchAnalysis:
        """Evaluate how well a structured job matches the candidate's profile."""
        matched_reqs: List[str] = []
        missing_reqs: List[str] = []
        missing_nice: List[str] = []
        risks: List[str] = []

        # ── 1. Skill & Qualification Match (35%) ──
        skill_score, m_skills, miss_skills = self._eval_skills(profile, job_info, raw_job)
        matched_reqs.extend(m_skills)
        missing_reqs.extend(miss_skills)

        # ── 2. Experience Match (20%) ──
        exp_score, exp_matched, exp_risk = self._eval_experience(profile, job_info)
        if exp_matched:
            matched_reqs.append(exp_matched)
        if exp_risk:
            risks.append(exp_risk)

        # ── 3. Role & Sector Match (20%) ──
        role_score, role_match_desc = self._eval_role_sector(profile, job_info, raw_job)
        if role_match_desc:
            matched_reqs.append(role_match_desc)

        # ── 4. Location Match (10%) ──
        loc_score = 90  # Default high for national/state public sector openings

        # ── 5. Salary Match (10%) ──
        salary_score = self._eval_salary(job_info, raw_job)

        # ── 6. Work Mode Match (5%) ──
        work_mode_score = 85  # Standard for public sector postings

        # Nice-to-have check
        if job_info.nice_to_have_skills:
            cand_skills = self._extract_candidate_terms(profile)
            for nth in job_info.nice_to_have_skills:
                if not any(t in nth.lower() for t in cand_skills):
                    missing_nice.append(nth)

        # ── Expiration / Deadline Check ──
        is_expired = False
        target_date = job_info.last_date or (raw_job.last_date if raw_job else None)
        if target_date and target_date < date.today():
            is_expired = True
            risks.append(f"Application deadline has passed ({target_date.strftime('%d %b %Y')}).")

        # ── Calculate Total Weighted Score ──
        cat_scores = CategoryScores(
            skill_match=int(skill_score),
            experience_match=int(exp_score),
            role_match=int(role_score),
            location_match=int(loc_score),
            salary_match=int(salary_score),
            work_mode_match=int(work_mode_score),
        )

        raw_total = (
            cat_scores.skill_match * self.WEIGHTS["skill"] +
            cat_scores.experience_match * self.WEIGHTS["experience"] +
            cat_scores.role_match * self.WEIGHTS["role"] +
            cat_scores.location_match * self.WEIGHTS["location"] +
            cat_scores.salary_match * self.WEIGHTS["salary"] +
            cat_scores.work_mode_match * self.WEIGHTS["work_mode"]
        )

        final_score = int(round(raw_total))
        if is_expired:
            final_score = min(final_score, 30)

        # ── Determine Recommendation ──
        if is_expired:
            rec = "SKIP"
            summary = "Application deadline has already expired."
        elif final_score >= 85:
            rec = "STRONG APPLY"
            summary = "Outstanding fit across qualifications, sector priority, and experience level."
        elif final_score >= 70:
            rec = "APPLY"
            summary = "Solid match for your qualifications with high probability of shortlisting."
        elif final_score >= 55:
            rec = "INVESTIGATE"
            summary = "Good partial match, but check specific eligibility criteria and missing skills."
        elif final_score >= 40:
            rec = "CONSIDER"
            summary = "Borderline match; may require additional domain preparation or exam prerequisites."
        else:
            rec = "SKIP"
            summary = "Low compatibility with your specified background and ranked career preferences."

        return JobMatchAnalysis(
            match_score=final_score,
            category_scores=cat_scores,
            matched_requirements=matched_reqs,
            missing_requirements=missing_reqs,
            missing_nice_to_have=missing_nice,
            potential_risks=risks,
            recommendation=rec,
            match_summary=summary
        )

    def _eval_skills(self, profile: Profile, job_info: StructuredJobInfo, raw_job: Optional[Job]) -> Tuple[float, List[str], List[str]]:
        """Evaluate educational and skill alignment."""
        cand_qual = (profile.qualification or "").lower().strip()
        if not cand_qual:
            return 75.0, ["Open eligibility / General category"], []

        # Candidate aliases
        aliases = [cand_qual]
        if "b.tech" in cand_qual or "btech" in cand_qual or "engineering" in cand_qual:
            aliases.extend(["b.tech", "b.e", "btech", "engineering", "b.e.", "bachelor of technology", "graduate in engineering"])
        elif "degree" in cand_qual or "graduate" in cand_qual or "bsc" in cand_qual or "ba" in cand_qual or "b.com" in cand_qual:
            aliases.extend(["graduate", "degree", "any graduate", "bachelor", "b.sc", "b.com", "b.a"])
        elif "diploma" in cand_qual:
            aliases.extend(["diploma", "polytechnic"])
        elif "12th" in cand_qual or "intermediate" in cand_qual:
            aliases.extend(["12th", "10+2", "intermediate", "hsc"])
        elif "10th" in cand_qual or "matric" in cand_qual:
            aliases.extend(["10th", "matric", "high school", "ssc"])

        # Check against job education requirements
        job_req_text = " ".join([
            job_info.job_title,
            " ".join(job_info.education_requirements),
            " ".join(job_info.must_have_skills),
            (raw_job.eligibility if raw_job else "") or ""
        ]).lower()

        matched: List[str] = []
        missing: List[str] = []

        # Open to all graduates?
        if any(g in job_req_text for g in ["any graduate", "any degree", "graduation in any", "bachelor's degree in any", "degree in any discipline"]):
            matched.append(f"Qualification '{profile.qualification}' satisfies 'Any Graduate' criteria.")
            return 95.0, matched, []

        # Exact match
        matched_alias = None
        for alias in aliases:
            if alias in job_req_text:
                matched_alias = alias
                break

        if matched_alias:
            matched.append(f"Verified Qualification: {profile.qualification} matches job requirement.")
            return 95.0, matched, []

        # Partial keyword check
        if any(word in job_req_text for word in cand_qual.split() if len(word) > 3):
            matched.append(f"Related field match with {profile.qualification}.")
            return 75.0, matched, []

        # If must have specific degree and candidate didn't match
        missing.append(f"Requires: {', '.join(job_info.education_requirements[:2]) if job_info.education_requirements else 'Specialized qualification'}")
        return 40.0, matched, missing

    def _eval_experience(self, profile: Profile, job_info: StructuredJobInfo) -> Tuple[float, Optional[str], Optional[str]]:
        """Evaluate candidate experience level vs job seniority."""
        cand_exp = (profile.experience_level or "Fresher").lower()
        job_exp = (job_info.experience_required or "").lower()

        if "fresher" in cand_exp or "0-1" in cand_exp:
            if any(f in job_exp for f in ["fresher", "0-", "entry", "trainee", "assistant", "no experience", "any"]):
                return 100.0, "Perfect for fresh graduates / entry level candidates.", None
            elif any(e in job_exp for e in ["5+", "8+", "senior manager", "chief", "director"]):
                return 40.0, None, "Requires significant prior professional experience."
            else:
                return 80.0, "Entry level criteria compatible.", None
        else:
            return 90.0, "Experience level aligns with role requirements.", None

    def _eval_role_sector(self, profile: Profile, job_info: StructuredJobInfo, raw_job: Optional[Job]) -> Tuple[float, Optional[str]]:
        """Evaluate ranked sector preference match."""
        interests = profile.interests or []
        if not interests:
            return 80.0, "Matches general public career openings."

        combined_text = f"{job_info.job_title} {job_info.company} {(raw_job.source if raw_job else '')}".lower()

        sector_keywords = {
            "Defence": ["defence", "army", "navy", "air force", "bsf", "crpf", "cisf", "itbp", "ssb", "drdo", "mod", "nda", "cds", "afcat"],
            "PSU": ["psu", "ongc", "bhel", "ntpc", "iocl", "sail", "gail", "bpcl", "hpcl", "powergrid", "bel", "hal", "nhpc", "pgcil", "coal india"],
            "Railways": ["railway", "rrb", "rrc", "irctc", "loco pilot", "station master", "rail"],
            "Banking": ["bank", "sbi", "ibps", "rbi", "nabard", "sebi", "sidbi", "pnb", "bob", "canara", "po", "clerk", "specialist officer"],
            "IT/Software": ["software", "developer", "programmer", "it officer", "nic", "cdac", "system analyst", "computer", "data", "cyber", "informatics"],
            "UPSC": ["upsc", "civil services", "ias", "ips", "ifs", "capf", "nda", "cds", "epfo", "ies"],
            "SSC": ["ssc", "cgl", "chsl", "mts", "cpo", "je", "stenographer", "selection post"],
            "State Govt": ["psc", "state", "panchayat", "patwari", "talathi", "vyapam", "hssc", "bssc", "uppsc", "mpsc", "kpsc", "rpsc"],
            "Teaching": ["teacher", "professor", "lecturer", "tgt", "pgt", "prt", "ugc", "net", "set", "kendriya vidyalaya", "kvs", "nvs"],
            "Judiciary": ["court", "judge", "judiciary", "law officer", "legal assistant", "prosecution", "advocate"],
            "Medical": ["doctor", "nurse", "medical officer", "aiims", "ayush", "pharmacist", "health", "hospital"]
        }

        for rank_idx, sector in enumerate(interests):
            keywords = sector_keywords.get(sector, [sector.lower()])
            if any(kw in combined_text for kw in keywords):
                if rank_idx == 0:
                    return 100.0, f"🎯 Top Priority Sector #{rank_idx + 1} ({sector}) matched!"
                elif rank_idx == 1:
                    return 90.0, f"⭐ Priority Sector #{rank_idx + 1} ({sector}) matched."
                elif rank_idx == 2:
                    return 80.0, f"📌 Priority Sector #{rank_idx + 1} ({sector}) matched."
                else:
                    return 70.0, f"Preferred Sector ({sector}) matched."

        return 50.0, None

    def _eval_salary(self, job_info: StructuredJobInfo, raw_job: Optional[Job]) -> float:
        """Evaluate compensation level."""
        salary_text = (job_info.salary.raw_text if job_info.salary else "") or (raw_job.salary if raw_job else "") or ""
        if not salary_text:
            return 80.0
        if any(w in salary_text.lower() for w in ["level 10", "level 11", "level 12", "level 13", "level 14", "scale iii", "scale iv", "7th cpc"]):
            return 100.0
        if any(w in salary_text.lower() for w in ["level 7", "level 8", "level 9", "scale i", "scale ii", "56,100", "44,900"]):
            return 90.0
        if any(w in salary_text.lower() for w in ["level 4", "level 5", "level 6", "25,500", "29,200", "35,400"]):
            return 80.0
        return 75.0

    @staticmethod
    def _extract_candidate_terms(profile: Profile) -> List[str]:
        terms = []
        if profile.qualification:
            terms.extend(re.findall(r"\w+", profile.qualification.lower()))
        if profile.interests:
            for i in profile.interests:
                terms.extend(re.findall(r"\w+", i.lower()))
        return [t for t in terms if len(t) > 2]
