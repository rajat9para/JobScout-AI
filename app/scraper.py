"""Web scrapers for government job portals.

Design: Extract large text blocks and pass to Gemini for structured extraction.
This is resilient to site layout changes — no brittle CSS selectors.

Active Sources (verified working):
  - SarkariResult.com     ✅ 161K+ chars of job data
  - FreeJobAlert.com      ✅ 249K+ chars of job data
  - SarkariExam.com       ✅ Government exam portal
  - RojgarResult.com      ✅ Sarkari Naukri aggregator

Removed (broken/empty):
  - ncs.gov.in            ❌ Returns 404
  - employmentnews.gov.in ❌ Nearly empty pages (~2.9K chars)
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

# cloudscraper bypasses Cloudflare/WAF blocks on government portals
# Falls back gracefully if not installed
try:
    import cloudscraper
    _cloudscraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    _cloudscraper = None
    CLOUDSCRAPER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Multiple User-Agents for retry on block
USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
]

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENTS[0],
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
}

REQUEST_TIMEOUT = 45  # Increased for slow government sites
DELAY_BETWEEN_REQUESTS = 3  # Respectful delay


class BaseScraper(ABC):
    """Abstract base for all job source scrapers."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @abstractmethod
    def scrape(self) -> List[str]:
        """Return list of raw text chunks. Each chunk = one or more job postings."""
        pass

    def _fetch(self, url: str) -> Optional[str]:
        """Fetch URL with automatic retry using different User-Agents.
        
        Falls back to cloudscraper if requests gets blocked (403/Cloudflare).
        """
        for attempt, ua in enumerate(USER_AGENTS):
            try:
                logger.info(f"[{self.source_name}] Fetching: {url} (attempt {attempt + 1})")
                self.session.headers["User-Agent"] = ua
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)

                # Detect Cloudflare/WAF block pages before raising
                is_blocked = (
                    response.status_code in (403, 503)
                    or "cloudflare" in response.text.lower()[:500]
                    or "access denied" in response.text.lower()[:500]
                    or "captcha" in response.text.lower()[:500]
                )

                if is_blocked and CLOUDSCRAPER_AVAILABLE:
                    logger.warning(
                        f"[{self.source_name}] Blocked by WAF (status {response.status_code}), "
                        f"retrying with cloudscraper..."
                    )
                    try:
                        cs_response = _cloudscraper.get(url, timeout=REQUEST_TIMEOUT)
                        if len(cs_response.text) >= 500:
                            logger.info(
                                f"[{self.source_name}] ✅ cloudscraper success: "
                                f"{len(cs_response.text)} chars from {url}"
                            )
                            time.sleep(DELAY_BETWEEN_REQUESTS)
                            return cs_response.text
                    except Exception as cs_err:
                        logger.warning(f"[{self.source_name}] cloudscraper also failed: {cs_err}")

                response.raise_for_status()

                # Check if we got meaningful content (not just a block page)
                if len(response.text) < 500:
                    logger.warning(f"[{self.source_name}] Response too short ({len(response.text)} chars), retrying...")
                    time.sleep(2)
                    continue

                time.sleep(DELAY_BETWEEN_REQUESTS)
                logger.info(f"[{self.source_name}] Fetched {len(response.text)} chars from {url}")
                return response.text
            except requests.RequestException as e:
                logger.warning(f"[{self.source_name}] Fetch attempt {attempt + 1} failed {url}: {e}")
                if attempt < len(USER_AGENTS) - 1:
                    time.sleep(2)

        logger.error(f"[{self.source_name}] All fetch attempts failed for {url}")
        return None


    def _clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip() and len(line.strip()) > 2]
        return "\n".join(lines)

    def _chunk_text(self, text: str, max_chars: int = 12000) -> List[str]:
        if len(text) <= max_chars:
            return [text]
        chunks = []
        lines = text.split("\n")
        current_chunk = []
        current_len = 0
        for line in lines:
            line_len = len(line) + 1
            if current_len + line_len > max_chars and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_len = line_len
            else:
                current_chunk.append(line)
                current_len += line_len
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        return chunks


class SarkariResultScraper(BaseScraper):
    """SarkariResult.com — high-frequency government job postings."""

    @property
    def source_name(self) -> str: return "sarkariresult.com"
    @property
    def base_url(self) -> str: return "https://www.sarkariresult.com"

    def scrape(self) -> List[str]:
        urls = [
            "https://www.sarkariresult.com/",
            "https://www.sarkariresult.com/latestjob/",
        ]
        all_chunks = []
        for url in urls:
            html = self._fetch(url)
            if html:
                text = self._clean_html(html)
                all_chunks.extend(self._chunk_text(text, max_chars=15000))
        return all_chunks


class FreeJobAlertScraper(BaseScraper):
    """FreeJobAlert.com — government jobs aggregator."""

    @property
    def source_name(self) -> str: return "freejobalert.com"
    @property
    def base_url(self) -> str: return "https://www.freejobalert.com"

    def scrape(self) -> List[str]:
        urls = [
            "https://www.freejobalert.com/government-jobs/",
            "https://www.freejobalert.com/latest-notifications/",
        ]
        all_chunks = []
        for url in urls:
            html = self._fetch(url)
            if html:
                text = self._clean_html(html)
                all_chunks.extend(self._chunk_text(text, max_chars=15000))
        return all_chunks


class SarkariExamScraper(BaseScraper):
    """SarkariExam.com — government exam and job notifications."""

    @property
    def source_name(self) -> str: return "sarkariexam.com"
    @property
    def base_url(self) -> str: return "https://www.sarkariexam.com"

    def scrape(self) -> List[str]:
        urls = [
            "https://www.sarkariexam.com/",
            "https://www.sarkariexam.com/latest-jobs",
        ]
        all_chunks = []
        for url in urls:
            html = self._fetch(url)
            if html:
                text = self._clean_html(html)
                all_chunks.extend(self._chunk_text(text, max_chars=15000))
        return all_chunks


class RojgarResultScraper(BaseScraper):
    """RojgarResult.com — Sarkari Naukri aggregator."""

    @property
    def source_name(self) -> str: return "rojgarresult.com"
    @property
    def base_url(self) -> str: return "https://www.rojgarresult.com"

    def scrape(self) -> List[str]:
        urls = [
            "https://www.rojgarresult.com/",
        ]
        all_chunks = []
        for url in urls:
            html = self._fetch(url)
            if html:
                text = self._clean_html(html)
                all_chunks.extend(self._chunk_text(text, max_chars=15000))
        return all_chunks


def get_all_scrapers() -> List[BaseScraper]:
    """Factory: returns all configured scrapers."""
    return [
        SarkariResultScraper(),
        FreeJobAlertScraper(),
        SarkariExamScraper(),
        RojgarResultScraper(),
    ]
