"""
ElEmpleo spider for TechJobs_Scraper_Colombia.

This module implements a spider specifically designed for scraping
job listings from elempleo.com, Colombia's leading job portal.

Website: https://www.elempleo.com
"""

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


class ElEmpleoSpider(BaseJobSpider):
    """Spider for scraping job listings from elempleo.com.

    This spider extracts job postings from elempleo.com, a major Colombian
    job portal. It handles the site's specific HTML structure and
    implements pagination.

    Attributes:
        name: Spider identifier (default: "elempleo").
        allowed_domains: Domains this spider is allowed to crawl.
        start_urls: Initial URLs to start crawling from.

    CSS Selectors:
        The spider uses specific selectors for elempleo.com's structure.
        These may need updating if the site redesigns.

    Example:
        >>> spider = ElEmpleoSpider()
        >>> result = spider.start()
        >>> print(f"Scraped {len(result.items)} jobs")
    """

    name = "elempleo"
    allowed_domains = {"elempleo.com", "www.elempleo.com"}

    # Generate start URLs for each search term
    start_urls = [
        "https://www.elempleo.com/co/ofertas-empleo/informatica/",
        "https://www.elempleo.com/co/ofertas-empleo/ingenieria/",
        "https://www.elempleo.com/co/ofertas-empleo/tecnologia/",
    ]

    # CSS selectors specific to elempleo.com
    SELECTORS = {
        # Main job listing container
        "job_list": ".sc-jKJlTe, .sc-gbluSB, article, .oferta, .job-offer, [class*='oferta']",
        # Individual job card
        "job_card": ".sc-jKJlTe, .sc-gbluSB, article, .oferta, .job-offer",
        # Job title
        "title": "h2 a, h3 a, .sc-fsQiph, .sc-bLitAg, [class*='titulo'] a, .title a",
        # Company name
        "company": ".sc-hpvprK, .sc-kMBXWB, [class*='empresa'], .company, .employer",
        # Job location
        "location": ".sc-jTiYzA, .sc-kfGZPT, [class*='ubicacion'], .location, .place",
        # Salary (if available)
        "salary": ".sc-cIrDgd, [class*='salario'], .salary, .wage",
        # Posted date
        "date": ".sc-kZaiwX, .sc-jwmkzK, [class*='fecha'], .date, .posted",
        # Link to job detail
        "url": "h2 a::attr(href), h3 a::attr(href), a::attr(href)",
        # Pagination
        "pagination": ".sc-hpvprK a, .pagination a, .pager a, a[rel='next'], .next",
        "next_page": "a[rel='next']::attr(href), .next::attr(href)",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the ElEmpleo spider.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.scraped_count = 0
        self.search_term = ""

    async def parse(self, response: Response) -> AsyncIterator[Any]:  # type: ignore[override]
        """Parse job listings from elempleo.com response.

        This method ONLY collects job detail URLs and handles pagination.
        For each job URL, it yields a Request to parse_detail().

        Args:
            response: Response object from elempleo.com.

        Yields:
            Request objects to parse_detail for full job information.
        """
        self.logger.info(f"Parsing listing page: {response.url}")

        self._extract_search_term(response.url)

        try:
            job_cards = response.css(self.SELECTORS["job_card"])

            if not job_cards:
                self.logger.warning(f"No job cards found on {response.url}")
                job_cards = response.css("article")
                if not job_cards:
                    job_cards = response.css("[class*='oferta']")

            self.logger.info(f"Found {len(job_cards)} job cards")

            for card in job_cards:
                try:
                    job_url = ""
                    for selector in ["h2 a::attr(href)", "h3 a::attr(href)", "a::attr(href)"]:
                        job_url = card.css(selector).get("")
                        if job_url:
                            break

                    if not job_url:
                        continue

                    job_url = self._validate_url(job_url)
                    if not job_url:
                        continue

                    from scrapling.spiders import Request

                    yield Request(job_url, callback=self.parse_detail, sid="stealth")  # type: ignore[arg-type]

                except Exception as e:
                    self.logger.error(f"Error extracting job URL: {e}")
                    continue

            async for next_request in self._handle_pagination(response):
                yield next_request

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
            title = self._safe_extract_detail(response, "h1::text, h2::text, .title::text")
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
        company = self._safe_extract_detail(response, ".company::text, .employer::text")
        location = self._safe_extract_detail(response, ".location::text, .place::text")
        salary = self._safe_extract_detail(response, ".salary::text, .wage::text")
        date_posted = self._safe_extract_detail(response, ".date::text, .posted::text")
        full_description = self._extract_description(response)

        score = calcular_score(
            titulo=title,
            descripcion=full_description,
            ubicacion=location or "",
            empresa=company or "",
        )
        detected_techs = extract_technologies(full_description)

        return {
            "site": "elempleo",
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
            ".description::text",
            ".job-details::text",
            "[class*='descripcion']::text",
            ".fc_mainText::text",
            ".sc-jKJlTe::text",
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

    def _parse_job_card(self, card: Any, page_url: str) -> dict[str, Any] | None:
        """Parse a single job card element.

        Args:
            card: Selector object for the job card.
            page_url: URL of the page containing this card.

        Returns:
            Dictionary with parsed job information or None if parsing fails.
        """
        try:
            # Extract basic information
            title = self._safe_extract(card, "h2 a::text, h3 a::text, .title::text")
            company = self._safe_extract(card, ".company::text, .employer::text")
            location = self._safe_extract(card, ".location::text, .place::text")
            salary = self._safe_extract(card, ".salary::text, .wage::text")
            date_posted = self._safe_extract(card, ".date::text, .posted::text")

            # Extract URL
            job_url = ""
            for selector in ["h2 a::attr(href)", "h3 a::attr(href)", "a::attr(href)"]:
                job_url = card.css(selector).get("")
                if job_url:
                    break

            # Validate URL
            job_url = self._validate_url(job_url)

            # Skip if no title or URL
            if not title or not job_url:
                return None

            # Calculate relevance score
            score = calcular_score(
                titulo=title,
                descripcion="",
                ubicacion=location or "",
                empresa=company or "",
            )

            # Build job dictionary
            job = {
                "site": "elempleo",
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
                "description": "",  # Would require fetching detail page
            }

            # Only return jobs with minimum score
            if score > 0:
                self.logger.debug(f"Job '{title}' scored {score}")
                return job

            return None

        except Exception as e:
            self.logger.error(f"Error in _parse_job_card: {e}")
            return None

    async def _handle_pagination(self, response: Response) -> AsyncIterator[Any]:
        """Handle pagination for job listing pages.

        Args:
            response: Current page response.

        Yields:
            Request objects for next pages.
        """
        try:
            # Try to find next page link
            next_selectors = [
                "a[rel='next']::attr(href)",
                ".next::attr(href)",
                ".pagination a:last-child::attr(href)",
                "a[title='Siguiente']::attr(href)",
            ]

            next_url = ""
            for selector in next_selectors:
                next_url = response.css(selector).get("")
                if next_url:
                    break

            if next_url:
                next_url = self._validate_url(next_url)
                if next_url:
                    self.logger.info(f"Following pagination to: {next_url}")

                from scrapling.spiders import Request

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
                if term.lower().replace(" ", "+") in url.lower():
                    self.search_term = term
                    return
            self.search_term = "General"
        except Exception:
            self.search_term = "General"




# Convenience function for quick scraping
def scrape_elempleo(max_pages: int = 5) -> list[dict[str, Any]]:
    """Scrape elempleo.com and return job listings.

    This is a convenience function for quick scraping without
    needing to manually run the spider.

    Args:
        max_pages: Maximum number of pages to scrape per category.

    Returns:
        List of job dictionaries with scoring.

    Example:
        >>> jobs = scrape_elempleo(max_pages=2)
        >>> print(f"Found {len(jobs)} jobs")
    """
    spider = ElEmpleoSpider()
    result = spider.start()

    jobs = []
    for item in result.items[: max_pages * 20]:  # Approximate 20 jobs per page
        jobs.append(item)

    return jobs
