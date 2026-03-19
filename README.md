# JobsColombia

> Tech job scoring and utilities for Colombia.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/CristianMz21/JobsColombia/actions/workflows/tests.yml/badge.svg)](https://github.com/CristianMz21/JobsColombia/actions/workflows/tests.yml)
[![Lint](https://github.com/CristianMz21/JobsColombia/actions/workflows/lint.yml/badge.svg)](https://github.com/CristianMz21/JobsColombia/actions/workflows/lint.yml)

## Description

JobsColombia is a Python library that provides scoring, classification, and utility functions for tech job listings in Colombia.

This library helps you:
- Score job listings based on relevance (technologies, keywords, modality)
- Classify jobs by score ranges
- Identify primary tech stacks from job descriptions
- Export and format job data to CSV

**Note:** This package does NOT include web scraping. Use any scraper library (like `jobs_scraper`, `linkedin-scraper`, or custom solutions) to fetch job data, then use this library to analyze and score them.

## Installation

```bash
pip install jobscolombia
```

Or with uv:

```bash
uv add jobscolombia
```

## Usage

```python
import pandas as pd
from jobscolombia import calcular_score, clasificar_score

# Score a job listing
score = calcular_score(
    title="Senior Python Developer",
    description="We need a Python developer with Django, PostgreSQL, and AWS experience",
    location="Bogota, Colombia",
    company="Tech Corp"
)
# score = 85 (example)

# Classify the score
category = clasificar_score(score)
# category = "Excelente" (score >= 70)

# Score a DataFrame of jobs
df["score"] = df.apply(
    lambda r: calcular_score(
        str(r.get("title", "")),
        str(r.get("description", "")),
        str(r.get("location", "")),
    ),
    axis=1,
)
```

## API Reference

### Scoring

- `calcular_score(title, description, location, company)` - Calculate job relevance score (0-100)
- `clasificar_score(score)` - Classify score into category (Bajo, Regular, Bueno, Excelente)
- `identificar_stack_principal(text)` - Identify main tech stack from text

### Utilities

- `columnas_export()` - Get standard column names for CSV export
- `generar_nombre_csv(prefix)` - Generate timestamped CSV filename
- `formatear_fecha(date)` - Format date for export

### Logging

- `setup_logger(name, log_dir)` - Configure logger for the application

See source code for full documentation.

## Project Structure

```
jobscolombia/
├── src/jobscolombia/
│   ├── __init__.py         # Package exports
│   ├── scoring.py         # Scoring and classification
│   ├── utils.py           # Utilities (CSV, dates)
│   ├── logger.py          # Logging setup
│   └── config.py          # Configuration
├── tests/                 # Unit tests
├── pyproject.toml        # Project configuration
├── CHANGELOG.md          # Version history
├── CONTRIBUTING.md       # Contribution guidelines
├── SECURITY.md           # Security policy
└── .github/
    └── workflows/         # GitHub Actions
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/jobscolombia --cov-report=term-missing
```

## Linting

```bash
# Check code
ruff check .

# Format code
ruff format .
```

## Type Checking

```bash
# Run mypy
mypy src/jobscolombia --ignore-missing-imports
```

## Security

```bash
# Run security audit
safety check
pip-audit
bandit -r src/jobscolombia
```

## Tech Stack

- **Python 3.11+** - Main language
- **Pandas** - Data manipulation
- **Ruff** - Linting and formatting
- **Pytest** - Testing framework

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **[Pandas](https://pandas.pydata.org/)** - Data analysis and manipulation tool
- **[Ruff](https://docs.astral.sh/ruff/)** - Fast Python linter and formatter
- **[Pytest](https://pytest.org/)** - Testing framework

## Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.
