"""Web scrapers for government job portals.

Design: Extract large text blocks and pass to Gemini for structured extraction.
This is resilient to site layout changes — no brittle CSS selectors.
"""
import logging
import time
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
}

REQUEST_TIMEOUT = 30
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
        try:
            logger.info(f"[{self.source_name}] Fetching: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            time.sleep(DELAY_BETWEEN_REQUESTS)
            return response.text
        except requests.RequestException as e:
            logger.error(f"[{self.source_name}] Fetch failed {url}: {e}")
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


class NCSscraper(BaseScraper):
    """National Career Service — official government portal."""

    @property
    def source_name(self) -> str: return "ncs.gov.in"
    @property
    def base_url(self) -> str: return "https://ncs.gov.in"

    def scrape(self) -> List[str]:
        urls = [
            "https://ncs.gov.in/job-search",
            "https://ncs.gov.in/individual-job-seeker",
        ]
        all_chunks = []
        for url in urls:
            html = self._fetch(url)
            if html:
                text = self._clean_html(html)
                all_chunks.extend(self._chunk_text(text))
        return all_chunks


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
            "https://www.freejobalert.com/",
        ]
        all_chunks = []
        for url in urls:
            html = self._fetch(url)
            if html:
                text = self._clean_html(html)
                all_chunks.extend(self._chunk_text(text, max_chars=15000))
        return all_chunks


class EmploymentNewsScraper(BaseScraper):
    """Employment News — official weekly gazette."""

    @property
    def source_name(self) -> str: return "employmentnews.gov.in"
    @property
    def base_url(self) -> str: return "https://employmentnews.gov.in"

    def scrape(self) -> List[str]:
        urls = [
            "https://employmentnews.gov.in/",
            "https://employmentnews.gov.in/latest-jobs",
        ]
        all_chunks = []
        for url in urls:
            html = self._fetch(url)
            if html:
                text = self._clean_html(html)
                all_chunks.extend(self._chunk_text(text))
        return all_chunks


def get_all_scrapers() -> List[BaseScraper]:
    """Factory: returns all configured scrapers."""
    return [
        NCSscraper(),
        SarkariResultScraper(),
        FreeJobAlertScraper(),
        EmploymentNewsScraper(),
    ]
