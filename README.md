# TechJobs Colombia

> Professional web scraper for tech job listings in Colombia.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/CristianMz21/JobsColombia/actions/workflows/tests.yml/badge.svg)](https://github.com/CristianMz21/JobsColombia/actions/workflows/tests.yml)
[![Lint](https://github.com/CristianMz21/JobsColombia/actions/workflows/lint.yml/badge.svg)](https://github.com/CristianMz21/JobsColombia/actions/workflows/lint.yml)

## Description

Scraping tool to extract and analyze tech job listings in Colombia from multiple job portals:

- LinkedIn
- Indeed
- elempleo.com
- computrabajo.com
- mitrabajo.co

## Features

- Multi-portal tech job extraction
- Scoring and classification system for job relevance
- Outsourcing company filtering (BairesDev, Turing, Crossover, etc.)
- Job deduplication
- Dynamic proxy support
- Anti-detection protection (Cloudflare bypass, User-Agent rotation)
- Professional logging
- CSV export

## Requirements

- Python 3.11+
- uv (package manager)

## Installation

```bash
# Clone the repository
git clone https://github.com/CristianMz21/JobsColombia.git
cd JobsColombia

# Install dependencies with uv
uv sync

# Optional: Install dev dependencies
uv sync --dev
```

## Usage

```bash
# Run the scraper
python main.py
```

The script will extract job listings and save them to a timestamped CSV file.

## Configuration

Configuration is located in `src/config.py`:

- **Search terms**: Keywords for job search
- **Scoring weights**: Weights for technologies, modality, experience
- **Anti-detection settings**: Delay between requests, timeouts, retries
- **Company blacklist**: Outsourcing companies to exclude

## Project Structure

```
JobsColombia/
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── config.py           # Centralized configuration
│   ├── logger.py           # Logging setup
│   ├── scoring.py          # Scoring system
│   ├── scraping.py         # Scraping functions
│   ├── utils.py            # Utilities
│   ├── utils_proxies.py    # Proxy management
│   └── scrapers/          # Portal spiders
│       ├── base.py
│       ├── computrabajo.py
│       └── elempleo.py
├── tests/                  # Unit tests
├── pyproject.toml         # Project configuration
├── ruff.toml              # Linting configuration
└── .github/
    └── workflows/         # GitHub Actions
        ├── tests.yml
        └── lint.yml
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

## Linting

```bash
# Check code
ruff check .

# Format code
ruff format .

# Auto-fix issues
ruff check --fix .
```

## Tech Stack

- **Python 3.11+** - Main language
- **Scrapling** - Web scraping framework
- **Pandas** - Data manipulation
- **JobSpy** - LinkedIn/Indeed scraping
- **Requests** - HTTP client
- **Ruff** - Linting and formatting
- **Pytest** - Testing framework

## Disclaimer

This project is for educational purposes only. Make sure to comply with the Terms of Service of the job portals before using this scraper.

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Contributions

Contributions are welcome. Please open an issue or pull request to suggest changes or improvements.
