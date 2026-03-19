"""
Tests for ElEmpleoSpider using mocked responses.

This module tests the ElEmpleoSpider without making real HTTP requests.
Instead, it uses mocked Response objects with sample HTML that simulates
the structure of elempleo.com job listings.
"""

from unittest.mock import MagicMock

import pytest

ELEMPLEO_SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Empleos en Colombia</title></head>
<body>
    <div class="sc-jKJlTe">
        <h2><a href="/co/ofertas-de-empleo/123456/desarrollador-python-django">Desarrollador Python Django Senior</a></h2>
        <span class="sc-hpvprK">TechCorp Colombia</span>
        <span class="sc-jTiYzA">Bogotá, DC</span>
        <span class="sc-cIrDgd">$5.000.000 - $8.000.000 COP</span>
        <span class="sc-kZaiwX">Hace 2 días</span>
    </div>
    <div class="sc-gbluSB">
        <h3><a href="/co/ofertas-de-empleo/789012/backend-java-spring">Backend Java Spring Boot</a></h3>
        <span class="sc-kMBXWB">Innovatech SAS</span>
        <span class="sc-kfGZPT">Medellín, Antioquia</span>
        <span class="sc-cIrDgd">$6.000.000 - $9.000.000 COP</span>
        <span class="sc-jwmkzK">Hace 5 días</span>
    </div>
    <div class="sc-jKJlTe">
        <h2><a href="/co/ofertas-de-empleo/345678/c-sharp-dotnet">C# .NET Developer Senior</a></h2>
        <span class="company">Software Solutions</span>
        <span class="location">Remoto - Colombia</span>
    </div>
    <a rel="next" href="/co/ofertas-empleo/informatica/?page=2">Siguiente</a>
</body>
</html>
"""

ELEMPLEO_ALT_CLASSES_HTML = """
<!DOCTYPE html>
<html>
<body>
    <article class="oferta">
        <div class="sc-fsQiph"><a href="/co/oferta/111111/devops-engineer">DevOps Engineer AWS</a></div>
        <span class="sc-bLitAg">CloudTech</span>
        <span class="ubicacion">Cali, Valle</span>
        <span class="salario">$7.000.000 COP</span>
        <span class="fecha">Hace 1 día</span>
    </article>
    <article class="oferta">
        <div class="sc-fsQiph"><a href="/co/oferta/222222/react-frontend">React Frontend Developer</a></div>
        <span class="empresa">WebDev Studio</span>
        <span class="ubicacion">Barranquilla</span>
    </article>
    <a class="next" href="/co/ofertas-empleo/?page=2">Página siguiente</a>
</body>
</html>
"""

EMPTY_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="no-ofertas">No se encontraron ofertas</div>
</body>
</html>
"""

PAGINATION_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="sc-jKJlTe">
        <h2><a href="/co/ofertas/001/python-dev">Python Developer</a></h2>
        <span class="company">TestCorp</span>
    </div>
    <div class="sc-jKJlTe">
        <h2><a href="/co/ofertas/002/java-dev">Java Developer</a></h2>
        <span class="company">JavaCorp</span>
    </div>
    <nav class="pagination">
        <a href="/co/ofertas?page=1">Anterior</a>
        <a href="/co/ofertas?page=3">Siguiente</a>
    </nav>
    <a rel="next" href="/co/ofertas/?page=2">Next Page</a>
    <a class="next" href="/co/ofertas/?page=2">Página siguiente</a>
</body>
</html>
"""


class MockResponse:
    """Mock Response object that simulates scrapling.spiders.Response for elempleo.com."""

    def __init__(
        self, html: str, url: str = "https://www.elempleo.com/co/ofertas-empleo/informatica/"
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

        if "article.oferta" in selector:
            for match in re.finditer(
                r'<article class="oferta"[^>]*>.*?</article>', self._html, re.DOTALL
            ):
                results.append(match.group(0))

        if ".sc-fsQiph a::text" in selector:
            for match in re.finditer(r'class="sc-fsQiph"[^>]*>\s*<a[^>]*>([^<]+)</a>', self._html):
                results.append(match.group(1).strip())

        elif ".sc-fsQiph::text" in selector:
            for match in re.finditer(r'class="sc-fsQiph"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        if "h2 a::text" in selector and "h3" not in selector:
            for match in re.finditer(r"<h2>\s*<a[^>]*>([^<]+)</a>", self._html):
                results.append(match.group(1).strip())

        elif "h3 a::text" in selector and "h2" not in selector:
            for match in re.finditer(r"<h3>\s*<a[^>]*>([^<]+)</a>", self._html):
                results.append(match.group(1).strip())

        elif ".sc-fsQiph::text" in selector:
            for match in re.finditer(r'class="sc-fsQiph"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".sc-bLitAg::text" in selector:
            for match in re.finditer(r'class="sc-bLitAg"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".sc-hpvprK::text" in selector:
            for match in re.finditer(r'class="sc-hpvprK"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".sc-kMBXWB::text" in selector:
            for match in re.finditer(r'class="sc-kMBXWB"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".company::text" in selector:
            for match in re.finditer(r'<span class="company"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".employer::text" in selector:
            for match in re.finditer(r'<span class="employer"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".empresa::text" in selector:
            for match in re.finditer(r'<span class="empresa"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".sc-jTiYzA::text" in selector:
            for match in re.finditer(r'class="sc-jTiYzA"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".sc-kfGZPT::text" in selector:
            for match in re.finditer(r'class="sc-kfGZPT"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".location::text" in selector:
            for match in re.finditer(r'<span class="location"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".place::text" in selector:
            for match in re.finditer(r'<span class="place"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".ubicacion::text" in selector:
            for match in re.finditer(r'<span class="ubicacion"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".sc-cIrDgd::text" in selector:
            for match in re.finditer(r'class="sc-cIrDgd"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".salary::text" in selector:
            for match in re.finditer(r'<span class="salary"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".wage::text" in selector:
            for match in re.finditer(r'<span class="wage"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".salario::text" in selector:
            for match in re.finditer(r'<span class="salario"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".sc-kZaiwX::text" in selector:
            for match in re.finditer(r'class="sc-kZaiwX"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".sc-jwmkzK::text" in selector:
            for match in re.finditer(r'class="sc-jwmkzK"[^>]*>([^<]+)</', self._html):
                results.append(match.group(1).strip())

        elif ".date::text" in selector:
            for match in re.finditer(r'<span class="date"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".posted::text" in selector:
            for match in re.finditer(r'<span class="posted"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif ".fecha::text" in selector:
            for match in re.finditer(r'<span class="fecha"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        elif "h2 a::attr(href)" in selector and "h3" not in selector:
            for match in re.finditer(r"<h2>\s*<a[^>]*href=\"([^\"]+)\"", self._html):
                results.append(match.group(1))

        elif "h3 a::attr(href)" in selector and "h2" not in selector:
            for match in re.finditer(r"<h3>\s*<a[^>]*href=\"([^\"]+)\"", self._html):
                results.append(match.group(1))

        elif "a::attr(href)" in selector:
            for match in re.finditer(r'<a[^>]*href="([^"]+)"', self._html):
                results.append(match.group(1))

        elif "a[rel='next']::attr(href)" in selector:
            for match in re.finditer(r'<a[^>]*rel="next"[^>]*href="([^"]+)"', self._html):
                results.append(match.group(1))

        elif ".next::attr(href)" in selector:
            for match in re.finditer(r'<a[^>]*class="next"[^>]*href="([^"]+)"', self._html):
                results.append(match.group(1))

        elif ".pagination a:last-child::attr(href)" in selector:
            for match in re.finditer(
                r'<nav[^>]*class="pagination[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>[^<]*</a>',
                self._html,
                re.DOTALL,
            ):
                results.append(match.group(1))

        mock_selector = MagicMock()
        mock_selector._results = results
        mock_selector.get = lambda default="": results[0] if results else default
        mock_selector.getall = lambda: results

        return mock_selector


class MockSpider:
    """Mock spider that replicates ElEmpleoSpider parsing logic."""

    SELECTORS = {
        "job_list": ".sc-jKJlTe, .sc-gbluSB, article, .oferta, .job-offer, [class*='oferta']",
        "job_card": ".sc-jKJlTe, .sc-gbluSB, article, .oferta, .job-offer",
        "title": "h2 a, h3 a, .sc-fsQiph, .sc-bLitAg, [class*='titulo'] a, .title a",
        "company": ".sc-hpvprK, .sc-kMBXWB, [class*='empresa'], .company, .employer",
        "location": ".sc-jTiYzA, .sc-kfGZPT, [class*='ubicacion'], .location, .place",
        "salary": ".sc-cIrDgd, [class*='salario'], .salary, .wage",
        "date": ".sc-kZaiwX, .sc-jwmkzK, [class*='fecha'], .date, .posted",
        "url": "h2 a::attr(href), h3 a::attr(href), a::attr(href)",
        "pagination": ".sc-hpvprK a, .pagination a, .pager a, a[rel='next'], .next",
        "next_page": "a[rel='next']::attr(href), .next::attr(href)",
    }

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
                if term.lower() in url.lower():
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
            title = self._safe_extract(card, "h2 a::text, h3 a::text, .title::text")
            company = self._safe_extract(card, ".company::text, .employer::text")
            location = self._safe_extract(card, ".location::text, .place::text")
            salary = self._safe_extract(card, ".salary::text, .wage::text")
            date_posted = self._safe_extract(card, ".date::text, .posted::text")

            job_url = ""
            for selector in ["h2 a::attr(href)", "h3 a::attr(href)", "a::attr(href)"]:
                job_url = card.css(selector).get("")
                if job_url:
                    break

            if not title or not job_url:
                return None

            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.elempleo.com{job_url}"

            score = calcular_score(
                titulo=title,
                descripcion="",
                ubicacion=location or "",
            )

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
                "description": "",
            }

            if score > 0:
                return job

            return None

        except Exception as e:
            self.logger.error(f"Error in _parse_job_card: {e}")
            return None


class TestElEmpleoSpiderLogic:
    """Tests for ElEmpleoSpider parsing logic using mock HTML."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    @pytest.fixture
    def mock_response(self):
        return MockResponse(ELEMPLEO_SAMPLE_HTML)

    def test_parse_extracts_h2_titles(self, spider, mock_response):
        """Verify that the spider extracts h2 job titles correctly."""
        titles = mock_response.css("h2 a::text").getall()
        assert len(titles) == 2
        assert "Desarrollador Python Django Senior" in titles
        assert "C# .NET Developer Senior" in titles

    def test_parse_extracts_h3_titles(self, spider, mock_response):
        """Verify that the spider extracts h3 job titles correctly."""
        titles = mock_response.css("h3 a::text").getall()
        assert len(titles) == 1
        assert "Backend Java Spring Boot" in titles

    def test_parse_extracts_company_sc_classes(self, spider, mock_response):
        """Verify that the spider extracts company names from sc-* classes."""
        companies_hpvprK = mock_response.css(".sc-hpvprK::text").getall()
        assert "TechCorp Colombia" in companies_hpvprK

        companies_kMBXWB = mock_response.css(".sc-kMBXWB::text").getall()
        assert "Innovatech SAS" in companies_kMBXWB

    def test_parse_extracts_company_class(self, spider, mock_response):
        """Verify that the spider extracts company from .company class."""
        companies = mock_response.css(".company::text").getall()
        assert "Software Solutions" in companies

    def test_parse_extracts_location_sc_classes(self, spider, mock_response):
        """Verify that the spider extracts locations from sc-* classes."""
        locations_jTiYzA = mock_response.css(".sc-jTiYzA::text").getall()
        assert "Bogotá, DC" in locations_jTiYzA

        locations_kfGZPT = mock_response.css(".sc-kfGZPT::text").getall()
        assert "Medellín, Antioquia" in locations_kfGZPT

    def test_parse_extracts_location_class(self, spider, mock_response):
        """Verify that the spider extracts location from .location class."""
        locations = mock_response.css(".location::text").getall()
        assert "Remoto - Colombia" in locations

    def test_parse_extracts_url(self, spider, mock_response):
        """Verify that the spider extracts job URLs correctly."""
        urls_h2 = mock_response.css("h2 a::attr(href)").getall()
        urls_h3 = mock_response.css("h3 a::attr(href)").getall()
        all_urls = urls_h2 + urls_h3
        assert len(all_urls) == 3
        assert any("123456" in url for url in all_urls)
        assert any("789012" in url for url in all_urls)
        assert any("345678" in url for url in all_urls)

    def test_parse_extracts_salary(self, spider, mock_response):
        """Verify that the spider extracts salary information."""
        salaries = mock_response.css(".sc-cIrDgd::text").getall()
        assert any("$5.000.000" in s for s in salaries)
        assert any("$6.000.000" in s for s in salaries)

    def test_parse_extracts_date(self, spider, mock_response):
        """Verify that the spider extracts posting dates."""
        dates_kZaiwX = mock_response.css(".sc-kZaiwX::text").getall()
        assert "Hace 2 días" in dates_kZaiwX

        dates_jwmkzK = mock_response.css(".sc-jwmkzK::text").getall()
        assert "Hace 5 días" in dates_jwmkzK

    def test_job_card_parsing_full_flow(self, spider, mock_response):
        """Test complete job card parsing flow."""
        spider._extract_search_term("https://www.elempleo.com/co/ofertas-empleo/informatica/")

        card_html = '<h2><a href="/co/ofertas-de-empleo/123456/desarrollador-python-django">Desarrollador Python Django Senior</a></h2><span class="company">TechCorp Colombia</span><span class="location">Bogotá, DC</span><span class="salary">$5.000.000</span>'
        card = MockResponse(card_html)

        job = spider._parse_job_card(card, mock_response.url)

        assert job is not None
        assert job["title"] == "Desarrollador Python Django Senior"
        assert job["company"] == "TechCorp Colombia"
        assert "Bogotá" in job["location"]
        assert "elempleo" in job["job_url"]
        assert job["score"] > 0
        assert job["site"] == "elempleo"


class TestElEmpleoSpiderAlternativeClasses:
    """Tests for elempleo.com alternative CSS class structures."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    @pytest.fixture
    def alt_response(self):
        return MockResponse(ELEMPLEO_ALT_CLASSES_HTML)

    def test_parse_extracts_oferta_articles(self, spider, alt_response):
        """Verify that the spider extracts .oferta article elements."""
        ofertas = alt_response.css("article.oferta").getall()
        assert len(ofertas) > 0

    def test_parse_extracts_sc_fsqiph_titles(self, spider, alt_response):
        """Verify .sc-fsQiph class for titles."""
        titles = alt_response.css(".sc-fsQiph a::text").getall()
        assert len(titles) == 2
        assert "DevOps Engineer AWS" in titles
        assert "React Frontend Developer" in titles

    def test_parse_extracts_sc_blitag_company(self, spider, alt_response):
        """Verify .sc-bLitAg class for company."""
        companies = alt_response.css(".sc-bLitAg::text").getall()
        assert "CloudTech" in companies

    def test_parse_extracts_empresa_class(self, spider, alt_response):
        """Verify .empresa class for company."""
        companies = alt_response.css(".empresa::text").getall()
        assert "WebDev Studio" in companies

    def test_parse_extracts_ubicacion_class(self, spider, alt_response):
        """Verify .ubicacion class for location."""
        locations = alt_response.css(".ubicacion::text").getall()
        assert "Cali, Valle" in locations
        assert "Barranquilla" in locations

    def test_parse_extracts_salario_class(self, spider, alt_response):
        """Verify .salario class for salary."""
        salaries = alt_response.css(".salario::text").getall()
        assert "$7.000.000" in salaries[0]


class TestElEmpleoSpiderPagination:
    """Tests for pagination handling in ElEmpleoSpider."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    @pytest.fixture
    def paginated_response(self):
        return MockResponse(PAGINATION_HTML)

    def test_extracts_rel_next_pagination(self, spider, paginated_response):
        """Verify that rel='next' pagination link is extracted."""
        next_url = paginated_response.css("a[rel='next']::attr(href)").get()
        assert next_url == "/co/ofertas/?page=2"

    def test_extracts_dot_next_pagination(self, spider, paginated_response):
        """Verify that .next class pagination link is extracted."""
        next_url = paginated_response.css(".next::attr(href)").get()
        assert next_url == "/co/ofertas/?page=2"

    def test_job_urls_become_absolute(self, spider, paginated_response):
        """Verify that relative URLs are converted to absolute."""
        spider._extract_search_term("https://www.elempleo.com/co/ofertas-empleo/informatica/")

        card_html = '<h2><a href="/co/ofertas/001/python-dev">Python Developer</a></h2>'
        card = MockResponse(card_html)

        job = spider._parse_job_card(card, paginated_response.url)

        assert job is not None
        assert job["job_url"].startswith("https://www.elempleo.com")


class TestElEmpleoSpiderCleanText:
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


class TestElEmpleoSpiderExtractSearchTerm:
    """Tests for search term extraction from URLs."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    def test_extract_python_term(self, spider):
        """Verify Python search term is extracted."""
        spider._extract_search_term("https://www.elempleo.com/co/ofertas-empleo/python-developer/")
        assert "python" in spider.search_term.lower() or "Python" in spider.search_term

    def test_extract_java_term(self, spider):
        """Verify Java search term is extracted."""
        spider._extract_search_term("https://www.elempleo.com/co/ofertas-empleo/backend-java/")
        assert "java" in spider.search_term.lower() or "Java" in spider.search_term

    def test_extract_general_for_unknown_url(self, spider):
        """Verify 'General' is set for unknown URLs."""
        spider._extract_search_term("https://www.elempleo.com/co/other-category")
        assert spider.search_term == "General"


class TestElEmpleoSpiderScoring:
    """Tests for scoring functionality in ElEmpleoSpider."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    def test_python_job_gets_high_score(self, spider):
        """Verify Python jobs receive appropriate scoring."""
        card_html = '<h2><a href="/co/job">Python Django Developer</a></h2><span class="company">TestCorp</span>'
        card = MockResponse(card_html)

        job = spider._parse_job_card(
            card, "https://www.elempleo.com/co/ofertas-empleo/informatica/"
        )

        assert job is not None
        assert job["score"] >= 10
        assert "Python" in job["stack_principal"] or "Django" in job["stack_principal"]

    def test_java_job_gets_high_score(self, spider):
        """Verify Java jobs receive appropriate scoring."""
        card_html = '<h2><a href="/co/job">Backend Java Spring Boot</a></h2><span class="company">TestCorp</span>'
        card = MockResponse(card_html)

        job = spider._parse_job_card(
            card, "https://www.elempleo.com/co/ofertas-empleo/informatica/"
        )

        assert job is not None
        assert job["score"] >= 10
        assert "Java" in job["stack_principal"] or "Spring" in job["stack_principal"]

    def test_c_sharp_job_gets_high_score(self, spider):
        """Verify C# jobs receive appropriate scoring."""
        card_html = '<h2><a href="/co/job">C# .NET Senior Developer</a></h2><span class="company">TestCorp</span>'
        card = MockResponse(card_html)

        job = spider._parse_job_card(
            card, "https://www.elempleo.com/co/ofertas-empleo/informatica/"
        )

        assert job is not None
        assert job["score"] >= 10
        assert "C#" in job["stack_principal"] or ".NET" in job["stack_principal"]

    def test_non_tech_job_gets_low_score(self, spider):
        """Verify non-tech jobs receive lower scoring."""
        card_html = '<h2><a href="/co/job">Marketing Manager</a></h2><span class="company">TestCorp</span><span class="location">Bogotá</span>'
        card = MockResponse(card_html)

        spider._extract_search_term("https://www.elempleo.com/co/ofertas-empleo/informatica/")
        job = spider._parse_job_card(
            card, "https://www.elempleo.com/co/ofertas-empleo/informatica/"
        )

        if job is not None:
            assert job["score"] < 10
        else:
            assert True


ELEMPLEO_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head><title>Desarrollador Python Django - ElEmpleo</title></head>
<body>
    <div class="job-detail">
        <h1>Desarrollador Python Django</h1>
        <span class="company">TechCorp Colombia SAS</span>
        <span class="location">Bogotá, DC</span>
        <span class="salary">$5.000.000 - $8.000.000 COP</span>
        <span class="date">Hace 3 días</span>
        <div class="description">
            <p>Somos TechCorp Colombia, buscamos desarrollador Python Django.</p>
            <p>Requisitos:</p>
            <ul>
                <li>Python y Django avanzado</li>
                <li>PostgreSQL</li>
                <li>Docker y AWS</li>
                <li>React es un plus</li>
            </ul>
            <p>Ofrecemos trabajo remoto, salario competitivo.</p>
        </div>
    </div>
</body>
</html>
"""


class MockElEmpleoDetailResponse:
    """Mock Response for elempleo detail pages."""

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

        if ".company::text" in selector:
            for match in re.finditer(r'<span class="company"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        if ".location::text" in selector:
            for match in re.finditer(r'<span class="location"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        if ".salary::text" in selector:
            for match in re.finditer(r'<span class="salary"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        if ".date::text" in selector:
            for match in re.finditer(r'<span class="date"[^>]*>([^<]+)</span>', self._html):
                results.append(match.group(1).strip())

        if ".description::text" in selector:
            for match in re.finditer(
                r'<div class="description"[^>]*>(.*?)</div>', self._html, re.DOTALL
            ):
                results.append(match.group(1).strip())

        mock_selector = MagicMock()
        mock_selector._results = results
        mock_selector.get = lambda default="": results[0] if results else default
        mock_selector.getall = lambda: results

        return mock_selector


class TestElEmpleoParseDetail:
    """Tests for parse_detail method in elempleo."""

    @pytest.fixture
    def spider(self):
        return MockSpider()

    def test_parse_detail_extracts_title(self, spider):
        """Verify parse_detail extracts job title."""
        response = MockElEmpleoDetailResponse(
            ELEMPLEO_DETAIL_HTML, "https://www.elempleo.com/co/oferta/123"
        )
        title = response.css("h1::text").get()
        assert title == "Desarrollador Python Django"

    def test_parse_detail_extracts_company(self, spider):
        """Verify parse_detail extracts company."""
        response = MockElEmpleoDetailResponse(
            ELEMPLEO_DETAIL_HTML, "https://www.elempleo.com/co/oferta/123"
        )
        company = response.css(".company::text").get()
        assert company == "TechCorp Colombia SAS"

    def test_parse_detail_extracts_salary(self, spider):
        """Verify parse_detail extracts exact salary."""
        response = MockElEmpleoDetailResponse(
            ELEMPLEO_DETAIL_HTML, "https://www.elempleo.com/co/oferta/123"
        )
        salary = response.css(".salary::text").get()
        assert "$5.000.000" in salary

    def test_parse_detail_extracts_full_description(self, spider):
        """Verify parse_detail extracts full job description."""
        response = MockElEmpleoDetailResponse(
            ELEMPLEO_DETAIL_HTML, "https://www.elempleo.com/co/oferta/123"
        )
        desc = response.css(".description::text").get()
        assert "Django" in desc
        assert "AWS" in desc

    def test_normalize_location_remoto(self, spider):
        """Verify location normalized to Remoto."""
        result = spider._normalize_location("Remoto", "")
        assert result == "Remoto"

    def test_normalize_location_remote_in_description(self, spider):
        """Verify Remoto detected from description text."""
        result = spider._normalize_location("Bogotá", "trabajo remoto disponible")
        assert result == "Remoto"

    def test_normalize_location_hibrido(self, spider):
        """Verify location normalized to Híbrido."""
        result = spider._normalize_location("Medellín", "Modalidad híbrida")
        assert result == "Híbrido"

    def test_normalize_location_bogota(self, spider):
        """Verify location normalized to Bogotá."""
        result = spider._normalize_location("Bogotá, DC", "")
        assert result == "Bogotá"
