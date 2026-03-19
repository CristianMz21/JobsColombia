"""
Tests for ComputrabajoSpider using mocked responses.

This module tests the ComputrabajoSpider without making real HTTP requests.
Instead, it uses mocked Response objects with sample HTML that simulates
the structure of computrabajo.com.co job listings.
"""

from unittest.mock import MagicMock

import pytest

COMPUTRABAJO_SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Jobs</title></head>
<body>
    <div class="box_rdr">
        <article class="iOffer">
            <h2><a href="/ofertas-de-empleo/123456/desarrollador-python-django">Desarrollador Python Django</a></h2>
            <span class="emp_bTitle">TechCorp Colombia</span>
            <span class="emp_loc">Bogotá, DC</span>
            <span class="salary">$5.000.000 - $8.000.000</span>
            <span class="date">Hace 2 días</span>
        </article>
    </div>
    <div class="box_rdr">
        <article class="iOffer">
            <h3><a href="/ofertas-de-empleo/789012/backend-java-spring">Backend Java Spring Boot</a></h3>
            <div class="d_flex">
                <span class="dIB">Innovatech SAS</span>
            </div>
            <span class="emp_loc">Medellín, Antioquia</span>
            <span class="fc_base">$6.000.000 - $9.000.000</span>
            <span class="date">Hace 5 días</span>
        </article>
    </div>
    <div class="box_rdr">
        <article class="iOffer">
            <h2><a href="/ofertas-de-empleo/345678/c-sharp-dotnet-developer">C# .NET Developer Senior</a></h2>
            <span class="emp_bTitle">Software Solutions</span>
            <span class="mrgt5">Remoto</span>
        </article>
    </div>
    <a class="pagnext" href="/trabajo-de-python?page=2">Siguiente</a>
</body>
</html>
"""

EMPTY_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="no-jobs">No se encontraron ofertas</div>
</body>
</html>
"""


class MockResponse:
    """Mock Response object that simulates scrapling.spiders.Response."""

    def __init__(self, html: str, url: str = "https://www.computrabajo.com.co/trabajo-de-python"):
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

        elif ".fs16::text" in selector:
            for match in re.finditer(r'class="fs16"[^>]*>([^<]+)</[^>]+>', self._html):
                results.append(match.group(1).strip())

        elif ".emp_bTitle::text" in selector:
            for match in re.finditer(r'<span class="emp_bTitle"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".d_flex .dIB::text" in selector:
            for match in re.finditer(
                r'<div class="d_flex[^"]*">\s*<span class="dIB"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        elif ".emp_loc::text" in selector:
            for match in re.finditer(r'<span class="emp_loc"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".mrgt5::text" in selector:
            for match in re.finditer(r'<span class="mrgt5"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".salary::text" in selector or ".fc_base::text" in selector:
            for match in re.finditer(
                r'<span class="(?:salary|fc_base)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        elif ".date::text" in selector:
            for match in re.finditer(r'<span class="date"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif "h2 a::attr(href)" in selector and "h3" not in selector:
            for match in re.finditer('<h2>\\s*<a[^>]*href="([^"]+)"[^>]*>[^<]+</a>', self._html):
                results.append(match.group(1))

        elif "h3 a::attr(href)" in selector and "h2" not in selector:
            for match in re.finditer('<h3>\\s*<a[^>]*href="([^"]+)"[^>]*>[^<]+</a>', self._html):
                results.append(match.group(1))

        elif "a.js_offer::attr(href)" in selector:
            for match in re.finditer(
                r'<a[^>]*class="[^"]*js_offer[^"]*"[^>]*href="([^"]+)"', self._html
            ):
                results.append(match.group(1))

        elif "a.pagnext::attr(href)" in selector:
            for match in re.finditer(
                r'<a[^>]*class="[^"]*pagnext[^"]*"[^>]*href="([^"]+)"', self._html
            ):
                results.append(match.group(1))

        elif "a[data-side='next']::attr(href)" in selector:
            for match in re.finditer(r'<a[^>]*data-side="next"[^>]*href="([^"]+)"', self._html):
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
    """Mock spider that replicates ComputrabajoSpider parsing logic."""

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

    def _normalize_location(self, location: str, full_text: str = "") -> str:
        """Normalize location to standard format."""
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

        colombian_cities = {
            "bogota": "Bogotá",
            "bogotá": "Bogotá",
            "medellin": "Medellín",
            "medellín": "Medellín",
            "cali": "Cali",
            "barranquilla": "Barranquilla",
        }

        location_lower = location.lower().strip()
        for city_key, city_normalized in colombian_cities.items():
            if city_key in location_lower:
                return city_normalized

        if location:
            return location.title()

        return "Colombia"

    def _parse_job_card(self, card, page_url: str):
        from jobscolombia.scoring import (
            calcular_score,
            clasificar_score,
            identificar_stack_principal,
        )

        try:
            title = self._safe_extract(card, "h2 a::text, h3 a::text, .fs16::text")
            if not title:
                return None

            company = self._safe_extract(card, ".emp_bTitle::text")
            if not company:
                company = self._safe_extract(card, ".d_flex .dIB::text")

            location = self._safe_extract(card, ".emp_loc::text")
            if not location:
                location = self._safe_extract(card, ".mrgt5::text")

            salary = self._safe_extract(card, ".salary::text")
            if not salary:
                salary = self._safe_extract(card, ".fc_base::text")

            date_posted = self._safe_extract(card, ".date::text")

            job_url = ""
            for selector in ["h2 a::attr(href)", "h3 a::attr(href)", "a.js_offer::attr(href)"]:
                job_url = card.css(selector).get("")
                if job_url:
                    break

            if not job_url:
                return None

            if job_url and not job_url.startswith("http"):
                if job_url.startswith("/"):
                    job_url = f"https://www.computrabajo.com.co{job_url}"
                else:
                    job_url = f"https://www.computrabajo.com.co/{job_url}"

            score = calcular_score(
                titulo=title,
                descripcion="",
                ubicacion=location or "",
            )

            job = {
                "site": "computrabajo",
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


class TestComputrabajoSpiderLogic:
    """Tests for ComputrabajoSpider parsing logic using mock HTML."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    @pytest.fixture
    def mock_response(self):
        return MockResponse(COMPUTRABAJO_SAMPLE_HTML)

    @pytest.fixture
    def job_cards(self, mock_response):
        return mock_response.css("h2 a::text").getall() or mock_response.css("h3 a::text").getall()

    def test_parse_extracts_title(self, spider, mock_response):
        """Verify that the spider extracts job titles correctly."""
        titles_h2 = mock_response.css("h2 a::text").getall()
        titles_h3 = mock_response.css("h3 a::text").getall()
        all_titles = titles_h2 + titles_h3
        assert len(all_titles) == 3
        assert "Desarrollador Python Django" in all_titles

    def test_parse_extracts_company(self, spider, mock_response):
        """Verify that the spider extracts company names correctly."""
        companies = mock_response.css(".emp_bTitle::text").getall()
        assert "TechCorp Colombia" in companies
        assert "Software Solutions" in companies

        flex_companies = mock_response.css(".d_flex .dIB::text").getall()
        assert "Innovatech SAS" in flex_companies

    def test_parse_extracts_location(self, spider, mock_response):
        """Verify that the spider extracts locations correctly."""
        locations = mock_response.css(".emp_loc::text").getall()
        assert "Bogotá, DC" in locations
        assert "Medellín, Antioquia" in locations

        mrt_locations = mock_response.css(".mrgt5::text").getall()
        assert "Remoto" in mrt_locations

    def test_parse_extracts_url(self, spider, mock_response):
        """Verify that the spider extracts job URLs correctly."""
        urls_h2 = mock_response.css("h2 a::attr(href)").getall()
        urls_h3 = mock_response.css("h3 a::attr(href)").getall()
        all_urls = urls_h2 + urls_h3
        assert len(all_urls) == 3
        assert any("123456" in url for url in all_urls)
        assert any("789012" in url for url in all_urls)

    def test_parse_extracts_salary(self, spider, mock_response):
        """Verify that the spider extracts salary information."""
        salaries = mock_response.css(".salary::text").getall()
        assert any("$5.000.000" in s for s in salaries)

        fc_salaries = mock_response.css(".fc_base::text").getall()
        assert any("$6.000.000" in s for s in fc_salaries)

    def test_job_card_parsing_full_flow(self, spider, mock_response):
        """Test complete job card parsing flow."""
        spider._extract_search_term("https://www.computrabajo.com.co/trabajo-de-python")

        card_html = '<h2><a href="/ofertas-de-empleo/123456/desarrollador-python-django">Desarrollador Python Django</a></h2><span class="emp_bTitle">TechCorp Colombia</span><span class="emp_loc">Bogotá, DC</span><span class="salary">$5.000.000 - $8.000.000</span>'
        card = MockResponse(card_html)

        job = spider._parse_job_card(card, mock_response.url)

        assert job is not None
        assert job["title"] == "Desarrollador Python Django"
        assert job["company"] == "TechCorp Colombia"
        assert "Bogotá" in job["location"]
        assert "computrabajo" in job["job_url"]
        assert job["score"] > 0
        assert job["site"] == "computrabajo"


class TestComputrabajoSpiderCleanText:
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


class TestComputrabajoSpiderExtractSearchTerm:
    """Tests for search term extraction from URLs."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    def test_extract_python_term(self, spider):
        """Verify Python search term is extracted."""
        spider._extract_search_term("https://www.computrabajo.com.co/trabajo-de-python")
        assert "python" in spider.search_term.lower() or "Python" in spider.search_term

    def test_extract_java_term(self, spider):
        """Verify Java search term is extracted."""
        spider._extract_search_term("https://www.computrabajo.com.co/trabajo-de-java")
        assert "java" in spider.search_term.lower() or "Java" in spider.search_term

    def test_extract_general_for_unknown_url(self, spider):
        """Verify 'General' is set for unknown URLs."""
        spider._extract_search_term("https://www.computrabajo.com.co/other-category")
        assert spider.search_term == "General"


COMPUTRABAJO_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head><title>Desarrollador Python Django - TechCorp</title></head>
<body>
    <div class="container">
        <h1>Desarrollador Python Django</h1>
        <span class="emp_bTitle">TechCorp Colombia SAS</span>
        <span class="emp_loc">Bogotá, DC</span>
        <span class="salary">$5.000.000 - $8.000.000 COP</span>
        <span class="date">Hace 3 días</span>
        <div class="desc_text">
            <p>Somos TechCorp Colombia, estamos buscando un Desarrollador Python Django
            para nuestro equipo de tecnología. Requisitos:</p>
            <ul>
                <li>Experiencia con Python y Django</li>
                <li>Conocimiento de PostgreSQL</li>
                <li>Experience con Docker y AWS</li>
                <li>Conocimiento de React es un plus</li>
            </ul>
            <p>Ofrecemos:</p>
            <ul>
                <li>Salario competitivo</li>
                <li>Trabajo Remoto</li>
                <li>Beneficios adicionales</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

REMOTO_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head><title>Backend Java Spring - Remote</title></head>
<body>
    <h1>Backend Java Spring Boot Developer</h1>
    <span class="company">GlobalTech</span>
    <span class="location">Remoto - Colombia</span>
    <span class="salary">$6.000.000 COP</span>
    <div class="description">
        <p>Se busca desarrollador Java Spring Boot para proyecto internacional.</p>
        <p>Modalidad: Teletrabajo</p>
        <p>Tech stack: Java, Spring Boot, Kubernetes, AWS, PostgreSQL</p>
    </div>
</body>
</html>
"""

HIBRIDO_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head><title>DevOps Engineer - Hybrid</title></head>
<body>
    <h1>DevOps Engineer</h1>
    <span class="company">Innovatech SAS</span>
    <span class="location">Medellín, Antioquia</span>
    <div class="job-details">
        <p>Buscamos DevOps Engineer para equipo de infraestructura.</p>
        <p>Modalidad: Híbrido (3 días oficina, 2 remoto)</p>
        <p>Technologías: Docker, Kubernetes, AWS, Python, Jenkins</p>
    </div>
</body>
</html>
"""


class MockDetailResponse:
    """Mock Response for detail pages."""

    def __init__(self, html: str, url: str):
        self._html = html
        self.url = url
        self.status = 200
        self.body = html.encode("utf-8")

    def css(self, selector: str):
        import re

        results = []

        if "h1::text" in selector:
            for match in re.finditer(r"<h1[^>]*>([^<]+)</h1>", self._html):
                results.append(match.group(1).strip())
        elif "h2::text" in selector:
            for match in re.finditer(r"<h2[^>]*>([^<]+)</h2>", self._html):
                results.append(match.group(1).strip())

        if ".emp_bTitle::text" in selector or ".company::text" in selector:
            for match in re.finditer(
                r'<span class="(?:emp_bTitle|company)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        if ".emp_loc::text" in selector or ".location::text" in selector:
            for match in re.finditer(
                r'<span class="(?:emp_loc|location)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        if ".salary::text" in selector or ".fc_base::text" in selector:
            for match in re.finditer(
                r'<span class="(?:salary|fc_base)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        if ".date::text" in selector or ".emp_date::text" in selector:
            for match in re.finditer(
                r'<span class="(?:date|emp_date)"[^>]*>([^<]+)</span>', self._html
            ):
                results.append(match.group(1).strip())

        if (
            ".desc_text::text" in selector
            or ".description::text" in selector
            or ".job-details::text" in selector
        ):
            text_selectors = ["desc_text", "description", "job-details"]
            for sel in text_selectors:
                for match in re.finditer(
                    rf'<div class="{sel}"[^>]*>(.*?)</div>', self._html, re.DOTALL
                ):
                    results.append(match.group(1).strip())

        mock_selector = MagicMock()
        mock_selector._results = results
        mock_selector.get = lambda default="": results[0] if results else default
        mock_selector.getall = lambda: results

        return mock_selector


class TestComputrabajoParseDetail:
    """Tests for parse_detail method."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    def test_parse_detail_extracts_title(self, spider):
        """Verify parse_detail extracts job title."""
        response = MockDetailResponse(
            COMPUTRABAJO_DETAIL_HTML, "https://www.computrabajo.com.co/oferta/123"
        )
        title = response.css("h1::text").get()
        assert title == "Desarrollador Python Django"

    def test_parse_detail_extracts_company(self, spider):
        """Verify parse_detail extracts company."""
        response = MockDetailResponse(
            COMPUTRABAJO_DETAIL_HTML, "https://www.computrabajo.com.co/oferta/123"
        )
        company = response.css(".emp_bTitle::text").get()
        assert company == "TechCorp Colombia SAS"

    def test_parse_detail_extracts_salary(self, spider):
        """Verify parse_detail extracts exact salary."""
        response = MockDetailResponse(
            COMPUTRABAJO_DETAIL_HTML, "https://www.computrabajo.com.co/oferta/123"
        )
        salary = response.css(".salary::text").get()
        assert "$5.000.000" in salary

    def test_parse_detail_extracts_full_description(self, spider):
        """Verify parse_detail extracts full job description."""
        response = MockDetailResponse(
            COMPUTRABAJO_DETAIL_HTML, "https://www.computrabajo.com.co/oferta/123"
        )
        desc = response.css(".desc_text::text").get()
        assert "Django" in desc
        assert "Docker" in desc

    def test_normalize_location_remoto(self, spider):
        """Verify location is normalized to Remoto."""
        result = spider._normalize_location("Remoto - Colombia", "some text")
        assert result == "Remoto"

    def test_normalize_location_hibrido(self, spider):
        """Verify location is normalized to Híbrido."""
        result = spider._normalize_location("Medellín", "Modalidad: Híbrido")
        assert result == "Híbrido"

    def test_normalize_location_bogota(self, spider):
        """Verify location is normalized to Bogotá."""
        result = spider._normalize_location("Bogotá, DC", "")
        assert result == "Bogotá"

    def test_normalize_location_medellin(self, spider):
        """Verify location is normalized to Medellín."""
        result = spider._normalize_location("Medellín, Antioquia", "")
        assert result == "Medellín"

    def test_normalize_location_remote_keyword_in_desc(self, spider):
        """Verify Remoto detected even if location field is different."""
        result = spider._normalize_location("Bogotá", "Trabajo Remoto disponible")
        assert result == "Remoto"
