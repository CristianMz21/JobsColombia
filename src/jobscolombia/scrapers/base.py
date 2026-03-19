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
from collections.abc import Iterator
from typing import Any

from scrapling.fetchers import AsyncStealthySession
from scrapling.spiders import (
    Request,
    Response,
    SessionManager,
    Spider,
)

from jobscolombia.config import ANTIDETECTION_CONFIG, PROXIES


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
        import random

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
    allowed_domains: list[str] = []
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
        self._proxy_rotator = ProxyRotator(PROXIES if PROXIES else [])
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

        stealth_config = {
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
            AsyncStealthySession(**stealth_config),
            lazy=True,
        )

    def get_proxy_for_request(self) -> str | None:
        """Get a proxy for the next request.

        Returns:
            Proxy URL string, or None for direct connection.
        """
        return self._proxy_rotator.get_random_proxy()

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
        blocked_statuses = {401, 403, 407, 429, 444, 500, 502, 503, 504}
        if response.status in blocked_statuses:
            self.logger.warning(
                f"Blocked detected via status code: {response.status} for {response.url}"
            )
            return True

        # Check response content for blocking indicators
        try:
            body = response.body.decode("utf-8", errors="ignore").lower()
            blocked_keywords = [
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
            ]

            for keyword in blocked_keywords:
                if keyword in body:
                    self.logger.warning(
                        f"Blocked detected via keyword '{keyword}' for {response.url}"
                    )
                    return True

        except Exception as e:
            self.logger.error(f"Error checking response content: {e}")

        # Check for very short responses (potential blocking page)
        if len(response.body) < 500:
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
        request.kwargs.pop("proxy", None)

        # Add random delay before retry
        delay = self._random.uniform(
            self.config.min_delay * 2,
            self.config.max_delay * 2,
        )
        self.logger.info(f"Waiting {delay:.2f}s before retry...")
        await asyncio.sleep(delay)

        return request

    async def get_with_delay(self, url: str) -> Response:
        """Fetch a URL with a random human-like delay.

        This helper method adds randomness to request timing to avoid
        creating predictable patterns that could trigger anti-bot systems.

        Args:
            url: URL to fetch.

        Returns:
            Response object from the fetch.
        """
        # Random delay between requests (3-8 seconds by default)
        delay = self._random.uniform(
            self.config.min_delay,
            self.config.max_delay,
        )

        # Add some randomness to make it feel more human-like
        if self._random.random() > 0.7:
            delay *= self._random.uniform(0.8, 1.5)

        self.logger.debug(f"Waiting {delay:.2f}s before request to {url}")
        await asyncio.sleep(delay)

        # Use stealth session for protected websites
        async with AsyncStealthySession(
            headless=self.config.headless,
            block_webrtc=self.config.block_webrtc,
            hide_canvas=self.config.hide_canvas,
            solve_cloudflare=self.config.solve_cloudflare,
            locale=self.config.locale,
            timezone_id=self.config.timezone_id,
        ) as session:
            return await session.fetch(url)

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

    @abstractmethod
    async def parse(self, response: Response) -> Iterator[dict[str, Any]]:
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

    async def start_requests(self) -> Iterator[Request]:
        """Generate initial requests for the spider.

        This method can be overridden to add custom logic for generating
        initial requests, such as adding search parameters.

        Yields:
            Request objects for the start URLs.
        """
        for url in self.start_urls:
            yield Request(url, callback=self.parse, sid="stealth")


class JobSpiderMixin:
    """Mixin class providing common job spider utilities.

    This mixin provides helper methods for parsing job listings
    that can be shared across different spider implementations.
    """

    def parse_job_card(
        self,
        card: Any,
        selectors: dict[str, str],
    ) -> dict[str, Any]:
        """Parse a single job card element.

        Args:
            card: Selector object representing a job card.
            selectors: Dictionary of CSS selectors for job fields.

        Returns:
            Dictionary with parsed job information.
        """
        try:
            job = {
                "title": card.css(selectors.get("title", "h2::text")).get("").strip(),
                "company": card.css(selectors.get("company", ".company::text")).get("").strip(),
                "location": card.css(selectors.get("location", ".location::text")).get("").strip(),
                "salary": card.css(selectors.get("salary", ".salary::text")).get("").strip(),
                "date": card.css(selectors.get("date", ".date::text")).get("").strip(),
                "url": card.css(selectors.get("url", "a::attr(href)")).get(""),
            }

            # Clean up URL if it's a relative path
            if job["url"] and not job["url"].startswith("http"):
                job["url"] = f"https://{self.allowed_domains[0]}{job['url']}"

            return job

        except Exception as e:
            self.logger.error(f"Error parsing job card: {e}")
            return {}
