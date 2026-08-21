"""Gemini API integration for structured job extraction.

Uses Google Gemini 1.5 Flash (free tier: 15 RPM, 1M tokens/day).
Handles rate limiting with automatic retry and backoff.
"""
import hashlib
import json
import logging
import re
import time
import warnings
from typing import List
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
import google.generativeai as genai
from app.config import get_settings
from app.models import Job

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a specialized government job posting extractor. Extract ALL government job postings from the text below with COMPLETE details.

For EACH job posting found, extract these fields as JSON:
- title: Exact job title/post name (e.g., "Junior Engineer", "Clerk", "Assistant Professor")
- organization: Full recruiting department/organization name (e.g., "Railway Recruitment Board (RRB)", "State Bank of India (SBI)")
- description: 2-3 sentence summary of what the job is about, key highlights, and what the candidate will do
- eligibility: FULL eligibility text — qualifications, degrees, percentages, age limits, experience required (complete string, be thorough)
- age_limit: Age limit extracted separately (e.g., "18-32 years", "Max 35 years", "21-27 years (relaxation applicable)")
- degree_tags: Array of degrees mentioned (e.g., ["B.Tech", "B.E.", "BSc", "BCA", "Law", "MBA", "Any Graduate"])
- salary: EXACT pay scale or salary (e.g., "₹35,400–₹1,12,400/month (Level-6 CPC)", "₹20,000–₹60,000/month", "₹50,000/month + allowances")
- vacancies: EXACT number of posts (e.g., "4000 posts", "150 vacancies", "Not specified")
- selection_process: How candidates are selected (e.g., "Written Exam + Interview", "CBT + Physical Test", "UPSC Interview")
- exam_required: Specific exam name if any (e.g., "GATE 2026", "UPSC CSE", "SSC CGL", "IBPS CWE", or null)
- last_date: Application deadline in YYYY-MM-DD format. Infer year as 2026 if not given. Use null if not found.
- apply_link: Direct online application URL if present (e.g., "https://..."), otherwise null
- notification_link: URL to the full job notification/article on the source website if present, otherwise null

CRITICAL RULES:
1. ONLY extract GOVERNMENT jobs (PSU, Central Govt, State Govt, Railways, Banking, Defence, SSC, UPSC, Teaching, Public Sector)
2. IGNORE private companies, ads, navigation text, login prompts
3. Convert "15 Aug 2026" → "2026-08-15"
4. If eligibility says "B.Tech/B.E." include both in degree_tags
5. "Any Graduate" or "Any Branch" matches everything — add "Any Graduate" to degree_tags
6. For salary: include the pay band/level if mentioned (e.g., "Level-4", "Pay Band-2")
7. For vacancies: include category breakdown if mentioned (e.g., "500 posts (UR-250, OBC-135, SC-75, ST-40)")
8. notification_link and apply_link: extract any URLs that appear near the job listing — these are critical
9. Return ONLY a valid JSON array. NO markdown, NO explanations, NO code blocks.
10. If no jobs found, return: []

Source: {source}

Text to extract from:
---
{text}
---

JSON array output:"""


class JobExtractor:
    """Gemini-powered job extraction with rate-limit handling."""

    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay_seconds

    def extract(self, raw_text: str, source: str) -> List[Job]:
        """Extract jobs from raw text using Gemini."""
        if not raw_text or len(raw_text) < 200:
            logger.debug(f"[{source}] Text too short, skipping extraction")
            return []

        # Limit input to 8K chars so Gemini response fits in output tokens
        prompt = EXTRACTION_PROMPT.format(source=source, text=raw_text[:8000])

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=8192,
                    )
                )

                content = response.text.strip()
                jobs = self._parse_response(content, source, raw_text)
                logger.info(f"[{source}] Extracted {len(jobs)} jobs (attempt {attempt})")
                return jobs

            except Exception as e:
                error_str = str(e).lower()
                if "rate limit" in error_str or "quota" in error_str or "429" in error_str:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"[{source}] Gemini rate limit (attempt {attempt}), waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif any(k in error_str for k in ["not found", "404", "model", "invalid", "does not exist"]):
                    # Invalid model name — fail fast instead of retrying 3 times
                    logger.critical(
                        f"[{source}] ❌ CRITICAL: Gemini model '{self.model._model_name}' is INVALID or not found. "
                        f"Check GEMINI_MODEL env var. Valid models: gemini-1.5-flash, gemini-2.0-flash-lite. "
                        f"Error: {e}"
                    )
                    return []  # No point retrying with an invalid model
                else:
                    logger.error(f"[{source}] Gemini extraction failed (attempt {attempt}): {e}")
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)

        logger.error(f"[{source}] All extraction attempts failed")
        return []

    def parse_resume(self, resume_text: str) -> dict:
        """Parse resume text to extract qualification and skills.

        Returns dict with: qualification, degree, experience_level, skills
        """
        prompt = f"""Extract the following from this resume text:
- qualification: Highest degree (e.g., B.Tech, BSc, BCA, Law, MBA)
- degree: Branch/specialization if mentioned (e.g., CSE, Mechanical, Civil)
- experience_level: "Fresher" if no experience, "0-2 yrs" if 1-2 years, "2+ yrs" if more
- skills: Array of key skills mentioned

Return ONLY valid JSON. No markdown, no explanations.

Resume text:
---
{resume_text[:10000]}
---

JSON output:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=0.1, max_output_tokens=1000)
            )
            content = response.text.strip()
            # Extract JSON
            match = re.search(r'\{.*?\}', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {}
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            return {}

    def _parse_response(self, content: str, source: str, raw_text: str) -> List[Job]:
        """Parse Gemini's JSON response into Job objects.

        Handles truncated JSON gracefully by extracting individual
        complete JSON objects when the full array is malformed.
        """
        # Try 1: Parse the full content as JSON array (greedy match)
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if isinstance(data, list):
                    return self._build_jobs(data, source, raw_text)
            except json.JSONDecodeError:
                pass

        # Try 2: Parse as single object
        if content.strip().startswith("{"):
            try:
                data = json.loads(f"[{content}]")
                if isinstance(data, list):
                    return self._build_jobs(data, source, raw_text)
            except json.JSONDecodeError:
                pass

        # Try 3: Extract individual complete JSON objects from truncated response
        objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        data = []
        for obj_str in objects:
            try:
                obj = json.loads(obj_str)
                if isinstance(obj, dict) and obj.get("title"):
                    data.append(obj)
            except json.JSONDecodeError:
                continue

        if data:
            logger.info(f"[{source}] Recovered {len(data)} jobs from truncated JSON")
            return self._build_jobs(data, source, raw_text)

        logger.warning(f"[{source}] Could not parse any JSON. Raw: {content[:300]}")
        return []

    def _build_jobs(self, data: list, source: str, raw_text: str) -> List[Job]:
        """Convert parsed JSON objects into Job model instances."""
        jobs = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if not item.get("title"):
                continue

            # Build dedup hash
            hash_input = f"{source}:{item.get('title','')}:{item.get('organization','')}:{item.get('last_date','')}"
            raw_hash = hashlib.sha256(hash_input.encode()).hexdigest()

            # Parse date
            last_date = None
            if item.get("last_date"):
                try:
                    from datetime import datetime
                    last_date = datetime.strptime(str(item["last_date"]), "%Y-%m-%d").date()
                except ValueError:
                    pass

            # Parse degree_tags
            degree_tags = item.get("degree_tags", [])
            if isinstance(degree_tags, str):
                degree_tags = [t.strip() for t in degree_tags.split(",") if t.strip()]

            # apply_link fallback: use notification_link if apply_link not found
            apply_link = item.get("apply_link") or item.get("notification_link")
            notification_link = item.get("notification_link") or item.get("apply_link")

            job = Job(
                source=source,
                title=item.get("title", "Unknown"),
                organization=item.get("organization", "Unknown"),
                description=item.get("description"),
                eligibility=item.get("eligibility"),
                age_limit=item.get("age_limit"),
                degree_tags=degree_tags or None,
                salary=item.get("salary"),
                vacancies=item.get("vacancies"),
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
