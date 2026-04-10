"""
Base spider module for TechJobs_Scraper_Colombia.

This module provides the BaseJobSpider abstract class which implements
advanced anti-detection measures using Scrapling's AsyncStealthySession.

Key Features:
- Browser fingerprint spoofing via impersonation
- Cloudflare/anti-bot bypass with solve_cloudflare
- WebRTC leak prevention
- Canvas fingerprint randomization
- Automatic blocked request detection and retry
- Human-like delays between requests
"""

import asyncio
import random
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any

from scrapling.fetchers import AsyncStealthySession
from scrapling.spiders import (
    Request,
    Response,
    SessionManager,
    Spider,
)

from jobscolombia.config import ANTIDETECTION_CONFIG, PROXIES

# HTTP status codes that indicate blocking or rate limiting
BLOCKED_STATUS_CODES: frozenset[int] = frozenset({401, 403, 407, 429, 444, 500, 502, 503, 504})

# Minimum response body length to consider valid (500 bytes)
MIN_RESPONSE_LENGTH: int = 500

# Keywords that indicate blocking when found in response body
BLOCKED_KEYWORDS: tuple[str, ...] = (
    "access denied",
    "access to this page has been denied",
    "rate limit",
    "too many requests",
    "captcha",
    "blocked",
    "forbidden",
    "please verify you are human",
    "cloudflare",
    "attention required",
    "sorry, you have been blocked",
)


class ProxyRotator:
    """Rotates through a list of proxies to avoid rate limiting.

    This class manages a list of proxies and returns them in rotation.
    If no proxies are configured, returns None for direct connection.
    """

    def __init__(self, proxies: list[str] | None = None) -> None:
        """Initialize the proxy rotator.

        Args:
            proxies: List of proxy URLs (e.g., ['http://user:pass@ip:port']).
        """
        self.proxies = proxies or []
        self.index = 0

    def get_proxy(self) -> str | None:
        """Get the next proxy in rotation.

        Returns:
            Proxy URL string, or None if no proxies configured.
        """
        if not self.proxies:
            return None

        proxy = self.proxies[self.index]
        self.index = (self.index + 1) % len(self.proxies)
        return proxy

    def get_random_proxy(self) -> str | None:
        """Get a random proxy from the list.

        Returns:
            Random proxy URL string, or None if no proxies configured.
        """
        if not self.proxies:
            return None

        return random.choice(self.proxies)


class BaseJobSpider(Spider, ABC):
    """Abstract base spider for job portal scraping with advanced anti-detection.

    This class implements a robust scraping framework that mimics real browser
    behavior to avoid detection by anti-bot systems. It uses Scrapling's
    AsyncStealthySession with comprehensive stealth options.

    Attributes:
        name: Unique identifier for the spider.
        allowed_domains: List of domains this spider is allowed to crawl.
        concurrent_requests: Maximum number of concurrent requests.
        download_delay: Base delay between requests in seconds.

    Anti-Detection Features:
        - Headless browser with stealth configuration
        - WebRTC leak blocking
        - Canvas fingerprint randomization
        - Cloudflare challenge solving
        - Colombian locale and timezone spoofing
        - Automatic blocked request retry

    Example:
        >>> class MySpider(BaseJobSpider):
        ...     name = "my_spider"
        ...     start_urls = ["https://example.com/jobs"]
        ...
        ...     async def parse(self, response: Response):
        ...         for job in response.css('.job'):
        ...             yield {"title": job.css('h2::text').get()}
    """

    # Spider metadata - override in subclasses
    name: str = "base_job_spider"
    allowed_domains: set[str] = set()
    start_urls: list[str] = []

    # Concurrency settings
    concurrent_requests: int = ANTIDETECTION_CONFIG.concurrent_requests
    download_delay: float = ANTIDETECTION_CONFIG.min_delay

    # Retry configuration
    max_blocked_retries: int = ANTIDETECTION_CONFIG.max_retries

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the spider with anti-detection configuration.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.config = ANTIDETECTION_CONFIG
        self._random = random.Random()
        self._proxy_rotator = ProxyRotator(list(PROXIES) if PROXIES else [])
        super().__init__(*args, **kwargs)

    def configure_sessions(self, manager: SessionManager) -> None:
        """Configure the session manager with stealth sessions.

        This method sets up two types of sessions:
        1. HTTP session for fast requests (not currently used)
        2. Stealth session for protected websites

        Args:
            manager: SessionManager instance to configure.
        """
        proxy = self._proxy_rotator.get_proxy()

        stealth_config: dict[str, bool | int | str | None] = {
            "headless": self.config.headless,
            "block_webrtc": self.config.block_webrtc,
            "hide_canvas": self.config.hide_canvas,
            "solve_cloudflare": self.config.solve_cloudflare,
            "locale": self.config.locale,
            "timezone_id": self.config.timezone_id,
            "google_search": False,
            "disable_resources": True,
            "timeout": self.config.timeout * 1000,
        }

        if proxy:
            stealth_config["proxy"] = proxy
            self.logger.info(f"Using proxy: {proxy}")

        manager.add(
            "stealth",
            AsyncStealthySession(**stealth_config),  # type: ignore[arg-type]
            lazy=True,
        )

    async def is_blocked(self, response: Response) -> bool:
        """Detect if a response indicates blocking or rate limiting.

        This method checks both HTTP status codes and response content
        for signs of anti-bot measures.

        Args:
            response: Response object from the request.

        Returns:
            True if the response indicates blocking, False otherwise.
        """
        # Check HTTP status codes commonly used for blocking
        if response.status in BLOCKED_STATUS_CODES:
            self.logger.warning(
                f"Blocked detected via status code: {response.status} for {response.url}"
            )
            return True

        # Check response content for blocking indicators
        try:
            body = response.body.decode("utf-8", errors="ignore").lower()

            for keyword in BLOCKED_KEYWORDS:
                if keyword in body:
                    self.logger.warning(
                        f"Blocked detected via keyword '{keyword}' for {response.url}"
                    )
                    return True

        except UnicodeDecodeError as e:
            self.logger.error(f"Error decoding response content: {e}")

        # Check for very short responses (potential blocking page)
        if len(response.body) < MIN_RESPONSE_LENGTH:
            self.logger.warning(
                f"Unusually short response ({len(response.body)} bytes) from {response.url}"
            )

        return False

    async def retry_blocked_request(self, request: Request, response: Response) -> Request:
        """Modify a request before retrying after blocking detection.

        This method implements a fallback strategy where blocked requests
        are retried with a different session configuration.

        Args:
            request: Original request that was blocked.
            response: Response received that triggered blocking.

        Returns:
            Modified request ready for retry.
        """
        self.logger.info(f"Retrying blocked request: {request.url}")

        # Switch to stealth session for retry
        request.sid = "stealth"

        # Clear any existing proxy settings to get fresh connection
        if hasattr(request, "kwargs"):
            request.kwargs.pop("proxy", None)  # type: ignore[attr-defined]

        # Add random delay before retry
        delay = self._random.uniform(
            self.config.min_delay * 2,
            self.config.max_delay * 2,
        )
        self.logger.info(f"Waiting {delay:.2f}s before retry...")
        await asyncio.sleep(delay)

        return request

    def get_selectors(self) -> dict[str, Any]:
        """Get CSS selectors for common job listing elements.

        Override this method in subclasses to customize selectors
        for specific job portals.

        Returns:
            Dictionary of selector names to CSS selector strings.
        """
        return {
            "job_card": ".job, .offer, .listing, .vacancy, article",
            "title": "h2, h3, .title, .job-title, .position",
            "company": ".company, .employer, .company-name, .name",
            "location": ".location, .city, .place, [class*='location']",
            "salary": ".salary, .wage, .compensation, [class*='salary']",
            "date": ".date, .posted, .time, [class*='date']",
            "description": ".description, .summary, .snippet, [class*='desc']",
            "url": "a::attr(href)",
            "pagination": ".pagination a, .pager a, a[rel='next'], .next",
        }

    def _validate_url(self, url: str) -> str:
        """Validate and sanitize a URL, preventing path traversal attacks.

        Args:
            url: URL to validate (can be relative or absolute).

        Returns:
            Validated URL or empty string if invalid.
        """
        if not url:
            return ""

        # Check for path traversal attempts
        if ".." in url or url.startswith("/../"):
            self.logger.warning(f"Blocked potential path traversal in URL: {url}")
            return ""

        # If it's already an absolute URL, validate it
        if url.startswith("http"):
            return url

        # For relative URLs, prepend domain
        if url.startswith("/"):
            if self.allowed_domains:
                return f"https://{list(self.allowed_domains)[0]}{url}"
            return url

        # If it doesn't start with / or http, treat as relative path
        if self.allowed_domains:
            return f"https://{list(self.allowed_domains)[0]}/{url}"
        return url

    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and special characters.

        Args:
            text: Raw text to clean.

        Returns:
            Cleaned text.
        """
        if not text:
            return ""

        text = " ".join(text.split())
        text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        text = text.strip(".-—–_,;:")

        return text.strip()

    def _normalize_location(self, location: str, full_text: str = "") -> str:
        """Normalize location to standard format.

        Detects and categorizes:
        - Remoto/Remote/Teletrabajo -> Remoto
        - Híbrido/Hybrid -> Híbrido
        - Otherwise extracts exact Colombian city

        Args:
            location: Raw location text from the page.
            full_text: Full text to search for remote/hybrid keywords.

        Returns:
            Normalized location string.
        """
        combined = f"{location} {full_text}".lower()

        if any(
            word in combined
            for word in ["remoto", "remote", "teletrabajo", "trabajo remoto", "from home"]
        ):
            return "Remoto"

        if any(
            word in combined
            for word in ["híbrido", "hibrido", "híbrida", "hibrida", "hybrid", "mixto"]
        ):
            return "Híbrido"

        location_lower = location.lower().strip()
        for city_key, city_normalized in COLOMBIAN_CITIES.items():
            if city_key in location_lower:
                return city_normalized

        if location:
            return location.title()

        return "Colombia"

    def _safe_extract(self, element: Any, selector: str) -> str:
        """Safely extract text from an element.

        Args:
            element: Selector object to extract from.
            selector: CSS selector to use.

        Returns:
            Extracted and cleaned text, or empty string on error.
        """
        try:
            text = element.css(selector).get("")
            return self._clean_text(text) if text else ""
        except Exception:
            return ""

    @abstractmethod
    async def parse(self, response: Response) -> AsyncIterator[Any]:  # type: ignore[override]
        """Parse job listings from the response.

        This is an abstract method that must be implemented by subclasses.
        Each spider should yield job dictionaries with at least:
        - title: Job title
        - company: Company name
        - url: Link to job posting

        Args:
            response: Response object from the request.

        Yields:
            Dictionary containing job information.
        """
        pass

    async def start_requests(self) -> AsyncIterator[Request]:  # type: ignore[override]
        """Generate initial requests for the spider.

        This method can be overridden to add custom logic for generating
        initial requests, such as adding search parameters.

        Yields:
            Request objects for the start URLs.
        """
        for url in self.start_urls:
            yield Request(url, callback=self.parse, sid="stealth")  # type: ignore[arg-type]


COLOMBIAN_CITIES: dict[str, str] = {
    "bogota": "Bogotá",
    "bogotá": "Bogotá",
    "medellin": "Medellín",
    "medellín": "Medellín",
    "cali": "Cali",
    "barranquilla": "Barranquilla",
    "cartagena": "Cartagena",
    "cucuta": "Cúcuta",
    "bucaramanga": "Bucaramanga",
    "pereira": "Pereira",
    "manizales": "Manizales",
    "ibague": "Ibagué",
    "ibagué": "Ibagué",
    "neiva": "Neiva",
    "armenia": "Armenia",
    "villavicencio": "Villavicencio",
    "pasto": "Pasto",
    "monteria": "Montería",
    "sincelejo": "Sincelejo",
    "popayan": "Popayán",
    "tunja": "Tunja",
    "florencia": "Florencia",
    "quibdo": "Quibdó",
    "riohacha": "Riohacha",
    "santa marta": "Santa Marta",
    "valledupar": "Valledupar",
}

