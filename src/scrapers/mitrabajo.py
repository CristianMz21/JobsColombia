"""
MiTrabajo spider for TechJobs_Scraper_Colombia.

This module implements a spider specifically designed for scraping
job listings from mitrabajo.co, a growing Colombian job portal.

Website: https://www.mitrabajo.co
"""

import asyncio
import random
from collections.abc import Iterator
from typing import Any

from scrapling.spiders import Response

from src.config import SEARCH_TERMS
from src.scoring import calcular_score, clasificar_score, identificar_stack_principal
from src.scrapers.base import BaseJobSpider


class MiTrabajoSpider(BaseJobSpider):
    """Spider for scraping job listings from mitrabajo.co.

    This spider extracts job postings from mitrabajo.co, a growing
    Colombian job portal. It handles the site's specific HTML structure
    and implements pagination.

    Attributes:
        name: Spider identifier (default: "mitrabajo").
        allowed_domains: Domains this spider is allowed to crawl.
        start_urls: Initial URLs to start crawling from.

    CSS Selectors:
        The spider uses specific selectors for mitrabajo.co's structure.
        These may need updating if the site redesigns.

    Example:
        >>> spider = MiTrabajoSpider()
        >>> result = spider.start()
        >>> print(f"Scraped {len(result.items)} jobs")
    """

    name = "mitrabajo"
    allowed_domains = ["mitrabajo.co", "www.mitrabajo.co"]

    start_urls = [
        "https://www.mitrabajo.co/empleos-en-colombia/desarrollo-software",
        "https://www.mitrabajo.co/empleos-en-colombia/tecnologia-informacion",
        "https://www.mitrabajo.co/empleos-en-colombia/programacion",
    ]

    SELECTORS = {
        "job_list": ".job-item, .offer-item, article, .vacancy, [class*='job']",
        "job_card": ".job-item, .offer-item, article, .vacancy",
        "title": "h2 a::text, h3 a::text, .job-title::text, .title::text, .position a",
        "title_link": "h2 a::attr(href), h3 a::attr(href), .job-title a::attr(href)",
        "company": ".company-name::text, .employer::text, .company::text, [class*='empresa']::text",
        "location": ".location::text, .city::text, .place::text, [class*='ubicacion']::text",
        "salary": ".salary::text, .wage::text, .compensation::text, [class*='salario']::text",
        "date": ".date::text, .posted::text, .time-ago::text, [class*='fecha']::text",
        "description": ".description::text, .summary::text, .excerpt::text",
        "url": "h2 a::attr(href), h3 a::attr(href), a::attr(href)",
        "pagination": ".pagination a, .pager a, a[rel='next'], .next",
        "next_page": "a.next::attr(href), a[rel='next']::attr(href)",
        "page_button": ".pagination .active + * a::attr(href)",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the MiTrabajo spider.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.scraped_count = 0
        self.search_term = ""
        self.page_count = 0
        self.max_pages = 10

    async def parse(self, response: Response) -> Iterator[dict[str, Any]]:
        """Parse job listings from mitrabajo.co response.

        This method extracts job information from the page, applies
        scoring, and yields structured job dictionaries. It also
        handles pagination by following next page links.

        Args:
            response: Response object from mitrabajo.co.

        Yields:
            Dictionary containing job information with scoring:
            - site: Always "mitrabajo"
            - title: Job title
            - company: Company name
            - location: Job location
            - salary: Salary if available
            - date_posted: Posting date
            - job_url: Direct link to job posting
            - score: Calculated relevance score
            - clasificacion: Score category
            - stack_principal: Identified technology stack
            - search_term: Original search term used
        """
        self.logger.info(f"Parsing page: {response.url}")
        self.page_count += 1

        self._extract_search_term(response.url)

        try:
            job_cards = response.css(self.SELECTORS["job_card"])

            if not job_cards:
                job_cards = response.css("article")
                if not job_cards:
                    job_cards = response.css("[class*='job']")
                if not job_cards:
                    job_cards = response.css(".offer-item")

            self.logger.info(f"Found {len(job_cards)} job cards on page {self.page_count}")

            for card in job_cards:
                try:
                    job = self._parse_job_card(card, response.url)
                    if job:
                        self.scraped_count += 1
                        yield job
                except Exception as e:
                    self.logger.error(f"Error parsing job card: {e}")
                    continue

            if self.page_count < self.max_pages:
                async for next_request in self._handle_pagination(response):
                    yield next_request
            else:
                self.logger.info(f"Reached max pages ({self.max_pages})")

        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")

    def _parse_job_card(self, card: Any, page_url: str) -> dict[str, Any] | None:
        """Parse a single job card element.

        Args:
            card: Selector object for the job card.
            page_url: URL of the page containing this card.

        Returns:
            Dictionary with parsed job information or None if parsing fails.
        """
        try:
            title = self._safe_extract(card, "h2 a::text, h3 a::text, .job-title::text")
            if not title:
                title = self._safe_extract(card, ".title::text, .position::text")

            if not title:
                return None

            company = self._safe_extract(card, ".company-name::text")
            if not company:
                company = self._safe_extract(card, ".employer::text, .company::text")

            location = self._safe_extract(card, ".location::text")
            if not location:
                location = self._safe_extract(card, ".city::text, .place::text")

            salary = self._safe_extract(card, ".salary::text")
            if not salary:
                salary = self._safe_extract(card, ".wage::text, .compensation::text")

            date_posted = self._safe_extract(card, ".date::text")
            if not date_posted:
                date_posted = self._safe_extract(card, ".posted::text, .time-ago::text")

            job_url = ""
            for selector in ["h2 a::attr(href)", "h3 a::attr(href)", ".job-title a::attr(href)"]:
                job_url = card.css(selector).get("")
                if job_url:
                    break

            if not job_url:
                for href in card.css("a::attr(href)").getall():
                    if "/empleo/" in href or "/job/" in href or "/oferta/" in href:
                        job_url = href
                        break

            if not job_url:
                return None

            if job_url and not job_url.startswith("http"):
                if job_url.startswith("/"):
                    job_url = f"https://www.mitrabajo.co{job_url}"
                else:
                    job_url = f"https://www.mitrabajo.co/{job_url}"

            score = calcular_score(
                titulo=title,
                descripcion="",
                ubicacion=location or "",
                empresa=company or "",
            )

            job = {
                "site": "mitrabajo",
                "title": self._clean_text(title),
                "company": self._clean_text(company) if company else "No especificado",
                "location": self._clean_text(location) if location else "Colombia",
                "salary": self._clean_text(salary) if salary else "",
                "date_posted": self._clean_text(date_posted) if date_posted else "",
                "job_url": job_url,
                "score": score,
                "clasificacion": clasificar_score(score),
                "stack_principal": identificar_stack_principal(title),
                "search_term": self.search_term,
                "description": "",
            }

            if score > 0:
                self.logger.debug(f"Job '{title}' scored {score}")
                return job

            return None

        except Exception as e:
            self.logger.error(f"Error in _parse_job_card: {e}")
            return None

    async def _handle_pagination(self, response: Response) -> Iterator[Any]:
        """Handle pagination for job listing pages.

        MiTrabajo may use standard pagination or JavaScript-based navigation.
        This method tries multiple strategies.

        Args:
            response: Current page response.

        Yields:
            Request objects for next pages.
        """
        try:
            next_url = ""

            next_selectors = [
                "a.next::attr(href)",
                "a[rel='next']::attr(href)",
                ".pagination a:last-child::attr(href)",
                ".pagination .active + a::attr(href)",
                "a.pagination-next::attr(href)",
            ]

            for selector in next_selectors:
                next_url = response.css(selector).get("")
                if next_url:
                    break

            if not next_url:
                current_url = response.url
                page_match = None
                for pattern in [r"/pagina-(\d+)", r"/page=(\d+)", r"\?page=(\d+)"]:
                    import re

                    match = re.search(pattern, current_url)
                    if match:
                        page_match = int(match.group(1))
                        break

                if page_match is not None:
                    next_url = re.sub(
                        pattern,
                        f"/pagina-{page_match + 1}",
                        current_url,
                    )
                else:
                    base_url = current_url.rstrip("/")
                    separator = "/" if not any(x in base_url for x in ["?", "="]) else "&"
                    next_url = f"{base_url}{separator}pagina-2"

            if next_url:
                if not next_url.startswith("http"):
                    if next_url.startswith("/"):
                        next_url = f"https://www.mitrabajo.co{next_url}"
                    else:
                        next_url = f"https://www.mitrabajo.co/{next_url}"

                self.logger.info(f"Following pagination to: {next_url}")

                await asyncio.sleep(random.uniform(2, 5))

                from scrapling.spiders import Request

                yield Request(next_url, callback=self.parse, sid="stealth")

        except Exception as e:
            self.logger.error(f"Error handling pagination: {e}")

    def _extract_search_term(self, url: str) -> None:
        """Extract search term from URL.

        Args:
            url: URL to extract search term from.
        """
        try:
            url_lower = url.lower()
            for term in SEARCH_TERMS:
                term_parts = term.lower().split()
                for part in term_parts:
                    if part in url_lower:
                        self.search_term = term
                        return
            self.search_term = "General"
        except Exception:
            self.search_term = "General"

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


def scrape_mitrabajo(max_pages: int = 5) -> list[dict[str, Any]]:
    """Scrape mitrabajo.co and return job listings.

    This is a convenience function for quick scraping without
    needing to manually run the spider.

    Args:
        max_pages: Maximum number of pages to scrape per category.

    Returns:
        List of job dictionaries with scoring.

    Example:
        >>> jobs = scrape_mitrabajo(max_pages=3)
        >>> print(f"Found {len(jobs)} jobs")
    """
    spider = MiTrabajoSpider()
    spider.max_pages = max_pages
    result = spider.start()

    jobs = []
    for item in result.items:
        jobs.append(item)

    return jobs
