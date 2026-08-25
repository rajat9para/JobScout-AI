"""Groq LPU API integration for ultra-fast structured job extraction.

Uses Groq's high-speed inference engine with multi-model fallback:
- Primary: openai/gpt-oss-120b (high accuracy & structured JSON compliance)
- Fallbacks: openai/gpt-oss-20b, qwen/qwen3.6-27b, groq/compound-mini

Handles rate limits, reasoning tag stripping (<think>...</think>),
and markdown code fences automatically.
"""
import hashlib
import json
import logging
import re
import time
from typing import List, Optional

from groq import Groq

from app.config import get_settings
from app.models import Job

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a specialized Indian government job posting extractor. Extract ALL government job postings from the text below with COMPLETE details.

For EACH job posting found, extract these fields as JSON:
- title: Exact job title/post name (e.g., "Junior Engineer", "Clerk", "Assistant Professor", "Probationary Officer")
- organization: Full recruiting department/organization name (e.g., "Railway Recruitment Board (RRB)", "State Bank of India (SBI)", "UPSC", "SSC")
- description: 2-3 sentence summary of what the job is about, key duties, and scope of work
- eligibility: FULL eligibility text — qualifications, degrees, percentages, age criteria, experience required (be thorough)
- age_limit: Age limit (e.g., "18-32 years", "Max 35 years", "21-27 years (relaxation applicable)")
- degree_tags: Array of degrees mentioned (e.g., ["B.Tech", "B.E.", "BSc", "BCA", "Law", "MBA", "10th", "12th", "Diploma", "Any Graduate"])
- salary: EXACT pay scale or salary (e.g., "₹35,400–₹1,12,400/month (Level-6 CPC)", "₹20,000–₹60,000/month", "₹50,000/month + allowances")
- application_fee: Exact application / form fee (e.g., "₹500 (Gen/OBC), ₹250 (SC/ST/Ex-Servicemen)", "₹100", "No Fee / Nil")
- vacancies: EXACT number of posts (e.g., "4500 posts", "150 vacancies", "500 posts (UR-250, OBC-135, SC-75)")
- selection_process: How candidates are selected (e.g., "Written Exam + Interview", "Computer Based Test (CBT) + Physical Test", "Direct Interview")
- exam_required: Specific exam name if any (e.g., "GATE 2026", "UPSC CSE", "SSC CGL", "IBPS PO", or null)
- last_date: Application deadline in YYYY-MM-DD format. Infer year as 2026 if not given. Use null if not found.
- apply_link: Direct online application URL if present (e.g., "https://..."), otherwise null
- notification_link: URL to the official notification / notification PDF / article on the source website if present, otherwise null

CRITICAL RULES:
1. ONLY extract GOVERNMENT jobs (PSU, Central Govt, State Govt, Railways, Banking, Defence, SSC, UPSC, Teaching, Public Sector)
2. IGNORE private companies, commercial ads, navigation menus, login prompts
3. Standardize dates to YYYY-MM-DD (e.g. "30 Sept 2026" → "2026-09-30")
4. If eligibility says "B.Tech/B.E." include both in degree_tags
5. "Any Graduate" or "Any Branch" matches everything — add "Any Graduate" to degree_tags
6. Always capture application fee details if present in the text
7. Return ONLY a valid JSON array. NO markdown explanations, NO text outside JSON.
8. If no jobs found, return: []

Source: {source}

Text to extract from:
---
{text}
---

JSON array output:"""


class JobExtractor:
    """Groq LPU-powered job extraction with multi-model fallback and rate-limit handling."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.groq_api_key
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.primary_model = settings.groq_model or "openai/gpt-oss-120b"
        
        # Parse fallback models
        fallback_str = getattr(settings, "groq_fallback_models", "openai/gpt-oss-20b,qwen/qwen3.6-27b,groq/compound-mini")
        self.models_to_try = [self.primary_model]
        for m in fallback_str.split(","):
            m = m.strip()
            if m and m not in self.models_to_try:
                self.models_to_try.append(m)
                
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay_seconds

    def extract(self, raw_text: str, source: str) -> List[Job]:
        """Extract jobs from raw text using Groq AI with automatic model fallback."""
        if not raw_text or len(raw_text) < 150:
            logger.debug(f"[{source}] Text too short ({len(raw_text) if raw_text else 0} chars), skipping extraction")
            return []

        if not self.client:
            logger.critical(f"[{source}] ❌ Groq client not initialized. Check GROQ_API_KEY env var.")
            return []

        prompt = EXTRACTION_PROMPT.format(source=source, text=raw_text[:4500])

        # Try models in order (primary -> fallbacks)
        for model in self.models_to_try:
            for attempt in range(1, self.max_retries + 1):
                try:
                    logger.info(f"[{source}] Sending {len(raw_text[:4500])} chars to Groq model '{model}' (attempt {attempt})")
                    
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a precise data extractor for Indian government jobs. Respond ONLY with a valid JSON array."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.1,
                        max_tokens=2048,
                    )

                    content = response.choices[0].message.content or ""
                    jobs = self._parse_response(content, source, raw_text)
                    
                    if jobs:
                        logger.info(f"[{source}] ✅ Successfully extracted {len(jobs)} jobs using {model} (attempt {attempt})")
                        return jobs
                    else:
                        logger.info(f"[{source}] Model {model} returned 0 jobs for this chunk")
                        return []

                except Exception as e:
                    error_str = str(e).lower()
                    logger.warning(f"[{source}] Groq '{model}' error (attempt {attempt}): {e}")
                    
                    if "rate_limit" in error_str or "429" in error_str or "quota" in error_str:
                        wait_time = self.retry_delay * (2 ** attempt)
                        logger.warning(f"[{source}] Groq rate limit hit, backing off {wait_time}s...")
                        time.sleep(wait_time)
                    elif "model_not_found" in error_str or "does not exist" in error_str or "404" in error_str:
                        logger.warning(f"[{source}] Groq model '{model}' not found. Switching to fallback...")
                        break
                    else:
                        if attempt < self.max_retries:
                            time.sleep(self.retry_delay)

        logger.error(f"[{source}] All Groq extraction attempts failed across models: {self.models_to_try}")
        return []

    def parse_resume(self, resume_text: str) -> dict:
        """Parse resume text to extract qualification, specialization, and skills.

        Returns dict with: qualification, degree, experience_level, skills, preferred_sectors
        """
        if not self.client or not resume_text:
            return {}

        prompt = f"""Extract the following structured info from this resume text:
- qualification: Highest degree (e.g., "B.Tech", "BSc", "BCA", "Law", "MBA", "Diploma", "12th Pass")
- degree: Branch or specialization if mentioned (e.g., "Computer Science", "Mechanical", "Civil", "Finance")
- experience_level: "Fresher" if 0-1 yr or student, "0-2 yrs" if 1-2 years, "2+ yrs" if experienced
- skills: Array of top 5-8 key technical/domain skills
- preferred_sectors: Inferred interest sectors (e.g. ["IT/Software", "PSU", "Banking", "Railways", "Defence", "State Govt"])

Return ONLY valid JSON. No markdown, no conversational text.

Resume text:
---
{resume_text[:8000]}
---

JSON output:"""

        for model in self.models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a resume parser. Output valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1000,
                )
                content = response.choices[0].message.content or ""
                cleaned = self._clean_raw_text(content)
                
                match = re.search(r'\{.*?\}', cleaned, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            except Exception as e:
                logger.warning(f"Resume parsing attempt with {model} failed: {e}")
                continue

        return {}

    def _clean_raw_text(self, text: str) -> str:
        """Strip reasoning tags, markdown fences, and leading/trailing whitespace."""
        if not text:
            return ""
        # 1. Remove reasoning / thinking tags (e.g., <think>...</think>)
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # 2. Remove markdown code blocks (```json ... ``` or ``` ...)
        cleaned = re.sub(r'```(?:json)?\s*', '', cleaned)
        cleaned = cleaned.replace('```', '')
        return cleaned.strip()

    def _parse_response(self, content: str, source: str, raw_text: str) -> List[Job]:
        """Parse Groq's response into validated Job objects.

        Handles full JSON arrays, single objects, and truncated regex matches.
        """
        cleaned = self._clean_raw_text(content)

        # Strategy 1: Match full JSON array [...]
        json_array_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if json_array_match:
            try:
                data = json.loads(json_array_match.group(0))
                if isinstance(data, list):
                    return self._build_jobs(data, source, raw_text)
            except json.JSONDecodeError:
                pass

        # Strategy 2: Single JSON object {...}
        if cleaned.startswith("{") and cleaned.endswith("}"):
            try:
                data = json.loads(f"[{cleaned}]")
                if isinstance(data, list):
                    return self._build_jobs(data, source, raw_text)
            except json.JSONDecodeError:
                pass

        # Strategy 3: Regex recovery of individual complete JSON objects
        objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned, re.DOTALL)
        data = []
        for obj_str in objects:
            try:
                obj = json.loads(obj_str)
                if isinstance(obj, dict) and obj.get("title"):
                    data.append(obj)
            except json.JSONDecodeError:
                continue

        if data:
            logger.info(f"[{source}] Recovered {len(data)} jobs via regex recovery")
            return self._build_jobs(data, source, raw_text)

        logger.warning(f"[{source}] Could not parse JSON from model output. Snippet: {cleaned[:250]}")
        return []

    def _build_jobs(self, data: list, source: str, raw_text: str) -> List[Job]:
        """Convert parsed dictionary list into validated Job models."""
        jobs = []
        for item in data:
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("position") or item.get("Job Title")
            if not title:
                continue

            org = item.get("organization") or item.get("department") or item.get("Organization") or "Government Organization"

            # Parse last date
            last_date = None
            date_val = item.get("last_date") or item.get("Last Date") or item.get("deadline")
            if date_val:
                try:
                    from datetime import datetime
                    clean_date_str = str(date_val).strip()
                    # Handle YYYY-MM-DD
                    match_iso = re.search(r'\d{4}-\d{2}-\d{2}', clean_date_str)
                    if match_iso:
                        last_date = datetime.strptime(match_iso.group(0), "%Y-%m-%d").date()
                except Exception:
                    pass

            # Parse degree tags
            degree_tags = item.get("degree_tags") or item.get("degrees") or []
            if isinstance(degree_tags, str):
                degree_tags = [t.strip() for t in degree_tags.split(",") if t.strip()]

            # Links
            apply_link = item.get("apply_link") or item.get("apply_url") or item.get("notification_link")
            notification_link = item.get("notification_link") or item.get("official_pdf") or item.get("apply_link")

            # Unique deduplication hash
            hash_input = f"{source}:{title}:{org}:{str(last_date or '')}"
            raw_hash = hashlib.sha256(hash_input.encode()).hexdigest()

            job = Job(
                source=source,
                title=str(title).strip(),
                organization=str(org).strip(),
                description=item.get("description"),
                eligibility=item.get("eligibility") or item.get("qualification"),
                age_limit=item.get("age_limit"),
                degree_tags=degree_tags or None,
                salary=item.get("salary") or item.get("pay_scale"),
                application_fee=item.get("application_fee") or item.get("fee") or item.get("form_fees"),
                vacancies=item.get("vacancies") or item.get("posts") or item.get("Number of Posts"),
                selection_process=item.get("selection_process"),
                exam_required=item.get("exam_required"),
                last_date=last_date,
                apply_link=apply_link,
                notification_link=notification_link,
                raw_hash=raw_hash,
                raw_text=raw_text[:2000]
            )
            jobs.append(job)

        return jobs
