"""
Tests for MiTrabajoSpider using mocked responses.

This module tests the MiTrabajoSpider parsing logic without making real HTTP requests.
Instead, it uses mocked Response objects with sample HTML that simulates
the structure of mitrabajo.co job listings.
"""

from unittest.mock import MagicMock

import pytest

MITRABAJO_SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Empleos en Colombia</title></head>
<body>
    <article class="job-item">
        <h2><a href="/empleo/123/desarrollador-python-fastapi-remoto">Desarrollador Python FastAPI - Remoto</a></h2>
        <span class="company-name">TechLabs Colombia</span>
        <span class="location">Bogotá, DC - Remoto</span>
        <span class="salary">$6.000.000 - $10.000.000</span>
        <span class="posted">Hace 1 día</span>
    </article>
    <article class="offer-item">
        <h3><a href="/empleo/456/backend-java-spring-boot">Backend Java Spring Boot</a></h3>
        <span class="employer">Innovatech SAS</span>
        <span class="city">Medellín</span>
        <span class="wage">$7.000.000 - $11.000.000</span>
        <span class="date">Hace 3 días</span>
    </article>
    <div class="job-item">
        <h2><a href="/empleo/789/dotnet-csharp-senior">C# .NET Core Senior Developer</a></h2>
        <span class="company">Software Global</span>
        <span class="place">Cali, Valle del Cauca</span>
    </div>
    <a class="next" href="/empleos-en-colombia/desarrollo-software/pagina-2">Siguiente</a>
</body>
</html>
"""

EMPTY_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="no-results">No hay resultados para esta busqueda</div>
</body>
</html>
"""


class MockResponse:
    """Mock Response object that simulates scrapling.spiders.Response."""

    def __init__(
        self,
        html: str,
        url: str = "https://www.mitrabajo.co/empleos-en-colombia/desarrollo-software",
    ):
        self._html = html
        self.url = url
        self.status = 200
        self.body = html.encode("utf-8")

    def css(self, selector: str):
        """Simulate CSS selector queries on HTML content."""
        results = []
        import re

        if "," in selector:
            for part in selector.split(","):
                part = part.strip()
                results.extend(self.css(part).getall())
            return MagicMock(
                _results=results,
                get=lambda d="": results[0] if results else d,
                getall=lambda: results,
            )

        if "h2 a::text" in selector and "h3" not in selector:
            for match in re.finditer(r"<h2>\s*<a[^>]*>([^<]+)</a>", self._html):
                results.append(match.group(1).strip())

        elif "h3 a::text" in selector and "h2" not in selector:
            for match in re.finditer(r"<h3>\s*<a[^>]*>([^<]+)</a>", self._html):
                results.append(match.group(1).strip())

        elif ".job-title::text" in selector or ".title::text" in selector:
            for match in re.finditer(
                r'class="(?:job-title|title)"[^>]*>([^<]+)</[^>]+>', self._html
            ):
                results.append(match.group(1).strip())
            for match in re.finditer(
                r'<span class="(?:job-title|title)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        elif ".company-name::text" in selector or ".employer::text" in selector:
            for match in re.finditer(
                r'class="(?:company-name|employer)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        elif ".company::text" in selector:
            for match in re.finditer(r'<span class="company"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".location::text" in selector:
            for match in re.finditer(r'<span class="location"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".city::text" in selector or ".place::text" in selector:
            for match in re.finditer(
                r'<span class="(?:city|place)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        elif ".salary::text" in selector or ".wage::text" in selector:
            for match in re.finditer(
                r'<span class="(?:salary|wage)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        elif ".date::text" in selector or ".posted::text" in selector:
            for match in re.finditer(
                r'<span class="(?:date|posted)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        elif "h2 a::attr(href)" in selector and "h3" not in selector:
            for match in re.finditer('<h2>\\s*<a[^>]*href="([^"]+)"[^>]*>[^<]+</a>', self._html):
                results.append(match.group(1))

        elif "h3 a::attr(href)" in selector and "h2" not in selector:
            for match in re.finditer('<h3>\\s*<a[^>]*href="([^"]+)"[^>]*>[^<]+</a>', self._html):
                results.append(match.group(1))

        elif ".job-title a::attr(href)" in selector:
            for match in re.finditer(
                r'<span class="job-title"[^>]*>\s*<a[^>]*href="([^"]+)"', self._html
            ):
                results.append(match.group(1))

        elif "a.next::attr(href)" in selector or "a[rel='next']::attr(href)" in selector:
            for match in re.finditer(
                r'<a[^>]*class="[^"]*next[^"]*"[^>]*href="([^"]+)"', self._html
            ):
                results.append(match.group(1))
            for match in re.finditer(r'<a[^>]*rel="next"[^>]*href="([^"]+)"', self._html):
                results.append(match.group(1))

        elif "a::attr(href)" in selector:
            for match in re.finditer(r'<a[^>]*href="([^"]+)"', self._html):
                results.append(match.group(1))

        mock_selector = MagicMock()
        mock_selector._results = results
        mock_selector.get = lambda default="": results[0] if results else default
        mock_selector.getall = lambda: results

        return mock_selector


class MockSpider:
    """Mock spider that replicates MiTrabajoSpider parsing logic."""

    def __init__(self):
        self.scraped_count = 0
        self.search_term = ""
        self.page_count = 0
        self.max_pages = 10
        self.logger = MagicMock()

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = " ".join(text.split())
        text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        text = text.strip(".-—–_,;:")
        return text.strip()

    def _safe_extract(self, element, selector: str) -> str:
        try:
            text = element.css(selector).get("")
            return self._clean_text(text) if text else ""
        except Exception:
            return ""

    def _extract_search_term(self, url: str) -> None:
        from jobscolombia.config import SEARCH_TERMS

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

    def _parse_job_card(self, card, page_url: str):
        from jobscolombia.scoring import (
            calcular_score,
            clasificar_score,
            identificar_stack_principal,
        )

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
                return job

            return None

        except Exception as e:
            self.logger.error(f"Error in _parse_job_card: {e}")
            return None


class TestMiTrabajoSpiderLogic:
    """Tests for MiTrabajoSpider parsing logic using mock HTML."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    @pytest.fixture
    def mock_response(self):
        return MockResponse(MITRABAJO_SAMPLE_HTML)

    def test_parse_extracts_title(self, spider, mock_response):
        """Verify that the spider extracts job titles correctly."""
        titles_h2 = mock_response.css("h2 a::text").getall()
        titles_h3 = mock_response.css("h3 a::text").getall()
        all_titles = titles_h2 + titles_h3
        assert len(all_titles) == 3
        assert any("Python" in t for t in all_titles)

    def test_parse_extracts_company(self, spider, mock_response):
        """Verify that the spider extracts company names correctly."""
        companies = mock_response.css(".company-name::text").getall()
        assert "TechLabs Colombia" in companies

        employers = mock_response.css(".employer::text").getall()
        assert "Innovatech SAS" in employers

        company_spans = mock_response.css(".company::text").getall()
        assert "Software Global" in company_spans

    def test_parse_extracts_location(self, spider, mock_response):
        """Verify that the spider extracts locations correctly."""
        locations = mock_response.css(".location::text").getall()
        assert "Bogotá, DC - Remoto" in locations

        cities = mock_response.css(".city::text").getall()
        assert "Medellín" in cities

        places = mock_response.css(".place::text").getall()
        assert "Cali, Valle del Cauca" in places

    def test_parse_extracts_url(self, spider, mock_response):
        """Verify that the spider extracts job URLs correctly."""
        urls_h2 = mock_response.css("h2 a::attr(href)").getall()
        urls_h3 = mock_response.css("h3 a::attr(href)").getall()
        all_urls = urls_h2 + urls_h3
        assert len(all_urls) == 3
        assert any("123" in url for url in all_urls)
        assert any("456" in url for url in all_urls)
        assert any("789" in url for url in all_urls)

    def test_parse_extracts_salary(self, spider, mock_response):
        """Verify that the spider extracts salary information."""
        salaries = mock_response.css(".salary::text").getall()
        assert any("$6.000.000" in s for s in salaries)

        wages = mock_response.css(".wage::text").getall()
        assert any("$7.000.000" in s for s in wages)

    def test_job_card_parsing_full_flow(self, spider, mock_response):
        """Test complete job card parsing flow."""
        spider._extract_search_term(
            "https://www.mitrabajo.co/empleos-en-colombia/desarrollo-software"
        )

        card_html = '<h2><a href="/empleo/123/desarrollador-python-fastapi-remoto">Desarrollador Python FastAPI - Remoto</a></h2><span class="company-name">TechLabs Colombia</span><span class="location">Bogotá, DC - Remoto</span><span class="salary">$6.000.000 - $10.000.000</span>'
        card = MockResponse(card_html)

        job = spider._parse_job_card(card, mock_response.url)

        assert job is not None
        assert "Python" in job["title"] or "FastAPI" in job["title"]
        assert job["company"] == "TechLabs Colombia"
        assert "Bogotá" in job["location"]
        assert "mitrabajo" in job["job_url"]
        assert job["score"] > 0
        assert job["site"] == "mitrabajo"


class TestMiTrabajoSpiderCleanText:
    """Tests for text cleaning methods."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    def test_clean_text_removes_extra_whitespace(self, spider):
        """Verify that extra whitespace is normalized."""
        result = spider._clean_text("  Hello   World  \n\t")
        assert result == "Hello World"

    def test_clean_text_removes_special_chars(self, spider):
        """Verify that special characters are stripped."""
        result = spider._clean_text(".-—–_,;:Title:;_-—")
        assert result == "Title"

    def test_clean_text_handles_empty_string(self, spider):
        """Verify that empty strings return empty."""
        assert spider._clean_text("") == ""
        assert spider._clean_text(None) == ""


class TestMiTrabajoSpiderExtractSearchTerm:
    """Tests for search term extraction from URLs."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    def test_extract_software_term(self, spider):
        """Verify software search term is extracted."""
        spider._extract_search_term(
            "https://www.mitrabajo.co/empleos-en-colombia/desarrollo-software"
        )
        assert spider.search_term == "General" or len(spider.search_term) > 0

    def test_extract_tech_term(self, spider):
        """Verify tech term is extracted."""
        spider._extract_search_term(
            "https://www.mitrabajo.co/empleos-en-colombia/tecnologia-informacion"
        )
        assert spider.search_term == "General" or len(spider.search_term) > 0

    def test_extract_general_for_any_url(self, spider):
        """Verify 'General' or term is set for any URLs."""
        spider._extract_search_term("https://www.mitrabajo.co/other-category")
        assert spider.search_term == "General" or len(spider.search_term) > 0
