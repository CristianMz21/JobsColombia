# JobsColombia

**Tech job scoring and classification library for the Colombian market.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/CristianMz21/JobsColombia/actions/workflows/tests.yml/badge.svg)](https://github.com/CristianMz21/JobsColombia/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/CristianMz21/JobsColombia/branch/main/graph/badge.svg)](https://codecov.io/gh/CristianMz21/JobsColombia)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](http://mypy-lang.org/)

A Python library that scores, classifies, and enriches tech job listings using relevance algorithms tailored for the Colombian job market. Designed to help developers prioritize the most relevant opportunities.

## Features

- **Relevance Scoring** — Score jobs 0-100 based on tech keywords (Python, Java, AWS, Docker, etc.), seniority level, and work modality (remote/hybrid)
- **Tech Stack Identification** — Automatically detect the primary technology stack from job titles and descriptions
- **Score Classification** — Categorize jobs as Excellent / Good / Regular / Discarded
- **Company Blacklisting** — Filter out known low-quality or fraudulent employers
- **CSV Export** — Standardized export with timestamped filenames and consistent column ordering
- **Configurable Weights** — Customize scoring weights via environment variables or config file

## Installation

### From PyPI

```bash
pip install jobscolombia
```

### With uv

```bash
uv add jobscolombia
```

### From Source

```bash
git clone https://github.com/CristianMz21/JobsColombia.git
cd JobsColombia
uv sync --all-extras
uv pip install -e .
```

## Quick Start

```python
import pandas as pd
from jobscolombia import calcular_score, clasificar_score, identificar_stack_principal

# Score a single job
score = calcular_score(
    title="Senior Python Developer",
    description="Django, PostgreSQL, AWS, Docker - Remote position",
    location="Bogotá, Colombia",
    company="Tech Corp"
)

# Classify the score
category = clasificar_score(score)
# category = "Excelente"

# Identify the tech stack
stack = identificar_stack_principal("Python Developer with Django and FastAPI experience")
# stack = "Python/Django"

# Score an entire DataFrame
df["score"] = df.apply(
    lambda r: calcular_score(
        str(r.get("title", "")),
        str(r.get("description", "")),
        str(r.get("location", "")),
        empresa=str(r.get("company", "")),
    ),
    axis=1,
)
df["clasificacion"] = df["score"].apply(clasificar_score)
df["stack_principal"] = df.apply(
    lambda r: identificar_stack_principal(
        f"{r.get('title', '')} {r.get('description', '')}"
    ),
    axis=1,
)
```

## Scoring System

The scoring algorithm evaluates jobs based on:

| Category | Weight | Description |
|----------|--------|-------------|
| **Technology Match** | +5 to +20 per tech | Python, Java, AWS, Docker, React, etc. |
| **Seniority** | Junior: +5, Senior: -10 | Adjusts for experience level |
| **Modality** | Remote: +15, Hybrid: +5 | Work-from-home preference |
| **Exclusions** | Score = 0 | Vendedor, Mesero, etc. (non-tech roles) |
| **Blacklist** | Score = 0 | Known fraudulent companies |

Final score is capped at **100**.

## Configuration

JobsColombia uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_SCORE` | `100` | Maximum possible score |
| `REMOTO_WEIGHT` | `15` | Weight for remote work |
| `HIBRIDO_WEIGHT` | `5` | Weight for hybrid work |
| `JUNIOR_WEIGHT` | `5` | Weight for junior positions |
| `SENIOR_WEIGHT` | `-10` | Weight penalty for senior positions |

Or configure directly in `jobscolombia/config.py`:

```python
from jobscolombia.config import ScoringConfig

config = ScoringConfig(
    tech_weights={"python": 20, "java": 15, "aws": 10},
    modality_weights={"remoto": 15, "hibrido": 5},
    max_score=100,
)
```

## API Reference

### Core Functions

#### `calcular_score(titulo, descripcion="", ubicacion="", empresa="")`
Calculate relevance score (0-100) for a job listing.

#### `clasificar_score(score: int) -> str`
Classify score into: `"Excelente"` (≥70), `"Buena"` (45-69), `"Regular"` (20-44), `"Descartada"` (<20)

#### `identificar_stack_principal(text: str) -> str`
Identify primary tech stack from text. Returns: `"Python/Django"`, `"Java/Spring"`, `"C#/.NET"`, `"React/Frontend"`, or `"Otro/Mixto"`.

#### `calcular_score_detallado(titulo, descripcion="", ubicacion="", empresa="") -> dict`
Returns detailed breakdown with tech matches, seniority match, modality match, and exclusion flag.

### Utilities

#### `columnas_export() -> list[str]`
Returns ordered list of standard CSV column names.

#### `generar_nombre_csv(prefix: str = "jobs") -> str`
Generates timestamped filename: `jobs_2024-01-15_143052.csv`

#### `setup_logger(name: str, log_dir: str = "logs") -> logging.Logger`
Configures application logging with console and file handlers.

## Development Setup

```bash
# Clone and setup
git clone https://github.com/CristianMz21/JobsColombia.git
cd JobsColombia
uv sync --all-extras

# Run tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=src/jobscolombia --cov-report=term-missing

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy src/jobscolombia --ignore-missing-imports

# Security audit
uv run safety check
uv run bandit -r src/jobscolombia
```

## Project Structure

```
jobscolombia/
├── src/jobscolombia/
│   ├── __init__.py          # Public API exports
│   ├── config.py            # Scoring weights and configuration
│   ├── scoring.py           # Core scoring algorithms
│   ├── utils.py            # CSV and date utilities
│   ├── logger.py           # Logging configuration
│   └── scrapers/           # Portal-specific scrapers
│       ├── base.py          # Base spider with anti-detection
│       ├── elempleo.py     # elempleo.com scraper
│       ├── computrabajo.py  # computrabajo.com scraper
│       └── mitrabajo.py     # mitrabajo.co scraper
├── tests/                   # Unit and integration tests
├── pyproject.toml          # Project configuration
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── SECURITY.md             # Security policy
└── .github/
    └── workflows/           # CI/CD pipelines
```

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_scoring.py -v

# Run with coverage report
uv run pytest --cov=src/jobscolombia --cov-report=term-missing --cov-report=xml

# Run only tests matching pattern
uv run pytest -k "test_calcular"
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code style, testing, and pull requests.

## Security

For security vulnerabilities, please see [SECURITY.md](SECURITY.md) for responsible disclosure instructions.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and breaking changes.

## Acknowledgments

This project is built with and powered by the following open-source technologies:

### Core Dependencies

- [**pandas**](https://pandas.pydata.org/) — DataFrame manipulation and analysis for processing job listings at scale
- [**Scrapling**](https://github.com/Xpost2001/scrapling) — Async web scraping framework with built-in stealth features, browser fingerprinting, and Cloudflare bypass
- [**Playwright**](https://playwright.dev/) — Cross-browser automation for reliable web scraping
- [**curl_cffi**](https://github.com/Y潮China/curl_cffi) — Python binding for curl with TLS fingerprinting support, used by Scrapling for stealth HTTP requests
- [**nest_asyncio**](https://github.com/erdewit/nest_asyncio) — Enables nested event loops for running async scrapers in Jupyter/IPython environments

### Development Tools

- [**uv**](https://github.com/astral-sh/uv) — Fast Python package manager and resolver, written in Rust
- [**Ruff**](https://github.com/astral-sh/ruff) — Blazingly fast Python linter and formatter, written in Rust
- [**Pytest**](https://pytest.org/) — Comprehensive testing framework with plugins for async, coverage, and mocking
- [**mypy**](http://mypy-lang.org/) — Static type checker for Python, ensuring type safety across the codebase
- [**Bandit**](https://bandit.readthedocs.io/) — Security linter for Python code
- [**Safety**](https://safety.pycom.io/) — Security vulnerability scanner for Python dependencies

### Infrastructure

- [**GitHub Actions**](https://github.com/features/actions) — CI/CD pipelines for automated testing, linting, and publishing
- [**Codecov**](https://codecov.io/) — Code coverage tracking and reporting
- [**PyPI**](https://pypi.org/) — Package index for distribution

### Inspiration

The scoring and classification system was inspired by job search tools like **Jobscan**, **Resume Worded**, and various tech career platforms that help professionals prioritize relevant opportunities.

