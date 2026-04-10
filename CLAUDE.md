# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JobsColombia is a Python library that scrapes job listings from multiple Colombian job portals (LinkedIn, Indeed, elempleo.com, computrabajo.com, mitrabajo.co) and scores them based on relevance to tech roles.

## Common Commands

```bash
# Install dependencies (includes dev dependencies)
uv sync --all-extras

# Run all tests
pytest

# Run a single test file
pytest tests/test_scoring.py

# Run a single test function
pytest tests/test_scoring.py::test_calcular_score -v

# Run with coverage
pytest --cov=src/jobscolombia --cov-report=term-missing

# Lint code
ruff check .

# Format code
ruff format .

# Auto-fix linting issues
ruff check --fix .

# Type check
mypy src/jobscolombia --ignore-missing-imports

# Run security audits
safety check
bandit -r src/jobscolombia

# Run the scraper
python main.py
```

## Architecture

```
src/jobscolombia/
├── __init__.py          # Package exports (calcular_score, clasificar_score, identificar_stack_principal)
├── config.py            # All configuration: search terms, scoring weights, anti-detection settings
├── scoring.py           # Job scoring and classification logic
├── scraping.py          # Orchestrates multi-portal scraping, deduplication, and CSV export
├── logger.py            # Logging setup
├── utils.py             # CSV export helpers, date formatting
├── utils_proxies.py      # Proxy rotation utilities
└── scrapers/
    ├── base.py          # BaseJobSpider abstract class with anti-detection (Scrapling)
    ├── elempleo.py       # Spider for elempleo.com
    ├── computrabajo.py  # Spider for computrabajo.com
    └── mitrabajo.py      # Spider for mitrabajo.co
```

### Data Flow

1. `main.py` → `scrape_all_jobs_async()` orchestrates scraping
2. LinkedIn/Indeed → `scrape_jobs()` from `jobspy` library
3. Other portals → Custom `BaseJobSpider` subclasses using Scrapling's `AsyncStealthySession`
4. Results are combined into a DataFrame, deduplicated, scored, and exported

### Scoring System

Defined in `config.py` via `ScoringConfig` dataclass:
- **tech_weights**: Points per technology (Python, Java, C#, React, etc.)
- **seniority_weights**: Junior=positive, Senior=negative (market comparison)
- **modality_weights**: Remote jobs score higher
- **exclusion_words**: Words that discard jobs entirely (non-tech roles)
- **required_words**: Words that must be present to consider a job

### Anti-Detection

`BaseJobSpider` uses Scrapling's `AsyncStealthySession` with:
- Browser fingerprint spoofing
- Cloudflare challenge solving
- WebRTC leak blocking
- Canvas fingerprint randomization
- Colombian locale/timezone spoofing
- Proxy rotation support via `ProxyRotator` class

### Scoring Configuration

`SCORING_CONFIG` and `ANTIDETECTION_CONFIG` are global singleton instances in `config.py` that are used throughout the scrapers and scoring logic.

## Code Style

- Python 3.11+ with type hints
- Functions use snake_case, classes use PascalCase
- Use `dataclass` with `field(default_factory=...)` for configuration
- Scoring functions are exposed via `__init__.py` for public API
- Portals (spiders) are instantiated dynamically in `scrape_all_jobs_async()`
