"""
Computrabajo spider for TechJobs_Scraper_Colombia.

This module implements a spider specifically designed for scraping
job listings from computrabajo.com, a major Colombian job portal.

Website: https://www.computrabajo.com.co
"""

import asyncio
import random
from collections.abc import AsyncIterator, Iterator
from typing import Any

from scrapling.spiders import Response

from jobscolombia.config import SEARCH_TERMS
from jobscolombia.scoring import (
    calcular_score,
    clasificar_score,
    extract_technologies,
    identificar_stack_principal,
)
from jobscolombia.scrapers.base import BaseJobSpider


class ComputrabajoSpider(BaseJobSpider):
    """Spider for scraping job listings from computrabajo.com.co.

    This spider extracts job postings from computrabajo.com.co, a popular
    Colombian job portal. It handles the site's specific HTML structure,
    AJAX pagination, and implements rate limiting.

    Attributes:
        name: Spider identifier (default: "computrabajo").
        allowed_domains: Domains this spider is allowed to crawl.
        start_urls: Initial URLs to start crawling from.

    CSS Selectors:
        The spider uses specific selectors for computrabajo.com.co's structure.
        These may need updating if the site redesigns.

    Example:
        >>> spider = ComputrabajoSpider()
        >>> result = spider.start()
        >>> print(f"Scraped {len(result.items)} jobs")
    """

    name = "computrabajo"
    allowed_domains = {"computrabajo.com.co", "www.computrabajo.com.co"}

    start_urls = [
        "https://www.computrabajo.com.co/trabajo-de-informatica",
        "https://www.computrabajo.com.co/trabajo-de-tecnologia",
        "https://www.computrabajo.com.co/trabajo-de-sistemas",
    ]

    SELECTORS = {
        "job_list": ".box_rdr, .iOffer, article, .job, [class*='oferta']",
        "job_card": ".box_rdr, .iOffer, article, .job",
        "title": "h2 a::text, h3 a::text, .fs16::text, .offer_tt::text, a.js_offer",
        "title_link": "h2 a::attr(href), h3 a::attr(href), a.js_offer::attr(href)",
        "company": ".emp_bTitle::text, .company::text, .d_flex .dIB::text, [class*='empresa']",
        "location": ".emp_loc::text, .location::text, [class*='ubicacion']::text, .mrgt5::text",
        "salary": ".salary::text, .emp_salary::text, [class*='salario']::text, .fc_base::text",
        "date": ".date::text, .emp_date::text, [class*='fecha']::text",
        "description": ".desc_text::text, .description::text, [class*='descripcion']",
        "url": "h2 a::attr(href), h3 a::attr(href), a::attr(href)",
        "pagination": ".pag a, .pagination a, .next::attr(href), a[rel='next']",
        "next_page": "a.pagnext::attr(href), a[rel='next']::attr(href), .next a::attr(href)",
        "ajax_page": "a[data-page]::attr(data-page)",
        "page_param": ".pagging a::attr(onclick)",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Computrabajo spider.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.scraped_count = 0
        self.search_term = ""
        self.page_count = 0
        self.max_pages = 10

    async def parse(self, response: Response) -> AsyncIterator[Any]:  # type: ignore[override]
        """Parse job listings from computrabajo.com.co response.

        This method ONLY collects job detail URLs and handles pagination.
        For each job URL, it yields a Request to parse_detail().

        Args:
            response: Response object from computrabajo.com.co.

        Yields:
            Request objects to parse_detail for full job information.
        """
        self.logger.info(f"Parsing listing page: {response.url}")
        self.page_count += 1

        self._extract_search_term(response.url)

        try:
            job_cards = response.css(self.SELECTORS["job_card"])

            if not job_cards:
                job_cards = response.css("article")
                if not job_cards:
                    job_cards = response.css("[class*='oferta']")
                if not job_cards:
                    job_cards = response.css(".box_rdr")
                if not job_cards:
                    job_cards = response.css(".iOffer")

            self.logger.info(f"Found {len(job_cards)} job cards on page {self.page_count}")

            for card in job_cards:
                try:
                    job_url = ""
                    for selector in [
                        "h2 a::attr(href)",
                        "h3 a::attr(href)",
                        "a.js_offer::attr(href)",
                    ]:
                        job_url = card.css(selector).get("")
                        if job_url:
                            break

                    if not job_url:
                        continue

                    # Validate URL to prevent path traversal
                    job_url = self._validate_url(job_url)
                    if not job_url:
                        continue

                    from scrapling.spiders import Request

                    yield Request(job_url, callback=self.parse_detail, sid="stealth")  # type: ignore[arg-type]

                except Exception as e:
                    self.logger.error(f"Error extracting job URL: {e}")
                    continue

            if self.page_count < self.max_pages:
                async for next_request in self._handle_pagination(response):
                    yield next_request
            else:
                self.logger.info(f"Reached max pages ({self.max_pages})")

        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")

    async def parse_detail(self, response: Response) -> AsyncIterator[dict[str, Any]]:
        """Extract full job details from detail page.

        This method navigates to each job's detail page and extracts:
        - Title, Company, Location, Exact Salary, Full Description

        Args:
            response: Response object from job detail page.

        Yields:
            Dictionary containing complete job information.
        """
        self.logger.info(f"Parsing detail page: {response.url}")

        try:
            title = self._safe_extract_detail(response, "h1::text, h2::text, .offer_tt::text")
            if not title:
                return

            job_data = self._extract_job_fields(response, title)
            if job_data["score"] > 0:
                self.scraped_count += 1
                self.logger.debug(f"Job '{title}' scored {job_data['score']}")
                yield job_data

        except Exception as e:
            self.logger.error(f"Error parsing detail page: {e}")

    def _extract_job_fields(
        self, response: Response, title: str
    ) -> dict[str, Any]:
        """Extract all job fields from detail page.

        Args:
            response: Response object from job detail page.
            title: Already extracted job title.

        Returns:
            Dictionary with all job fields including score.
        """
        company = self._safe_extract_detail(response, ".emp_bTitle::text, .company::text")
        location = self._safe_extract_detail(response, ".emp_loc::text, .location::text")
        salary = self._safe_extract_detail(
            response, ".salary::text, .emp_salary::text, .fc_base::text"
        )
        date_posted = self._safe_extract_detail(response, ".date::text, .emp_date::text")
        full_description = self._extract_description(response)

        score = calcular_score(
            titulo=title,
            descripcion=full_description,
            ubicacion=location or "",
            empresa=company or "",
        )
        detected_techs = extract_technologies(full_description)

        return {
            "site": "computrabajo",
            "title": self._clean_text(title),
            "company": self._clean_text(company) if company else "No especificado",
            "location": self._normalize_location(location or "", full_description),
            "salary": self._clean_text(salary) if salary else "",
            "date_posted": self._clean_text(date_posted) if date_posted else "",
            "job_url": response.url,
            "score": score,
            "clasificacion": clasificar_score(score),
            "stack_principal": identificar_stack_principal(title + " " + full_description),
            "search_term": self.search_term,
            "description": "",
            "full_description": full_description,
            "detected_technologies": ", ".join(detected_techs),
        }

    def _extract_description(self, response: Response) -> str:
        """Extract full description from job detail page.

        Args:
            response: Response object from job detail page.

        Returns:
            Cleaned full description text.
        """
        desc_parts: list[str] = []
        desc_selectors = [
            ".desc_text::text",
            ".description::text",
            ".job-details::text",
            "[class*='descripcion']::text",
            ".fc_mainText::text",
        ]
        for selector in desc_selectors:
            desc_text = response.css(selector).get("")
            if desc_text:
                desc_parts.append(desc_text)

        return self._clean_text(" ".join(desc_parts))

    def _safe_extract_detail(self, response: Response, selector: str) -> str:
        """Safely extract text from detail page."""
        try:
            text = response.css(selector).get("")
            return self._clean_text(text) if text else ""
        except Exception:
            return ""

    async def _handle_pagination(self, response: Response) -> AsyncIterator[Any]:
        """Handle pagination for job listing pages.

        Computrabajo uses JavaScript-based pagination. This method tries
        multiple strategies to find and follow the next page.

        Args:
            response: Current page response.

        Yields:
            Request objects for next pages.
        """
        try:
            next_url = ""

            next_selectors = [
                "a.pagnext::attr(href)",
                "a[data-side='next']::attr(href)",
                ".pagination a:last-child::attr(href)",
                "a[rel='next']::attr(href)",
                ".next a::attr(href)",
            ]

            for selector in next_selectors:
                next_url = response.css(selector).get("")
                if next_url:
                    break

            if not next_url:
                current_url = response.url
                if "?page=" in current_url:
                    current_page = int(current_url.split("?page=")[1].split("&")[0].split("?")[0])
                    next_url = current_url.replace(
                        f"?page={current_page}", f"?page={current_page + 1}"
                    )
                else:
                    separator = "&" if "?" in current_url else "?"
                    next_url = f"{current_url}{separator}page=2"

            if next_url:
                next_url = self._validate_url(next_url)
                if next_url:
                    self.logger.info(f"Following pagination to: {next_url}")

                from scrapling.spiders import Request

                await asyncio.sleep(random.uniform(2, 5))
                yield Request(next_url, callback=self.parse, sid="stealth")  # type: ignore[arg-type]

        except Exception as e:
            self.logger.error(f"Error handling pagination: {e}")

    def _extract_search_term(self, url: str) -> None:
        """Extract search term from URL.

        Args:
            url: URL to extract search term from.
        """
        try:
            for term in SEARCH_TERMS:
                if term.lower().replace(" ", "-") in url.lower():
                    self.search_term = term
                    return
                if term.lower().split()[0] in url.lower():
                    self.search_term = term
                    return
            self.search_term = "General"
        except Exception:
            self.search_term = "General"



def scrape_computrabajo(max_pages: int = 5) -> list[dict[str, Any]]:
    """Scrape computrabajo.com.co and return job listings.

    This is a convenience function for quick scraping without
    needing to manually run the spider.

    Args:
        max_pages: Maximum number of pages to scrape per category.

    Returns:
        List of job dictionaries with scoring.

    Example:
        >>> jobs = scrape_computrabajo(max_pages=3)
        >>> print(f"Found {len(jobs)} jobs")
    """
    spider = ComputrabajoSpider()
    spider.max_pages = max_pages
    result = spider.start()

    jobs = []
    for item in result.items:
        jobs.append(item)

    return jobs
