# Agent Guidelines for jobs Project

## Project Overview
Python script that scrapes job listings from LinkedIn/Indeed, scores and ranks them, then exports to CSV.

## Quick Commands

### Running the Project
```bash
# Run the job scraper
python main.py
```

### Testing
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_scoring.py

# Run a single test function
pytest tests/test_scoring.py::test_calcular_score -v

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

### Linting & Formatting
```bash
# Run linting
ruff check .

# Run formatting
ruff format .

# Fix auto-fixable issues
ruff check --fix .

# Check specific file
ruff check main.py

# Check and fix specific file
ruff check --fix main.py
```

---

## Code Style Guidelines

### Python Version
- Target: Python 3.11+
- Use `.python-version` file

### Imports
- Standard library first, then third-party, then local
- Use absolute imports for local modules
- Group with blank line between groups
```python
import os
from datetime import datetime
from dataclasses import dataclass, field

import pandas as pd
from jobspy import scrape_jobs
```

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `utils.py`, `job_scraper.py` |
| Classes | PascalCase | `ScoringConfig` |
| Functions | snake_case | `calcular_score()` |
| Variables | snake_case | `search_term`, `tech_weights` |
| Constants | UPPER_SNAKE | `MAX_RESULTS`, `USER_AGENTS` |
| Type aliases | PascalCase | `JobDict`, `Score` |

### Type Hints
- Use type hints for function parameters and return values
- Use `dict` and `list` instead of `Dict`, `List` (Python 3.9+)
```python
def calcular_score(titulo: str, descripcion: str = "", ubicacion: str = "") -> int:
    ...
```

### Dataclasses
- Use `@dataclass` for configuration and data containers
- Use `field(default_factory=...)` for mutable defaults
```python
@dataclass
class ScoringConfig:
    tech_weights: dict = field(
        default_factory=lambda: {"python": 15}
    )
```

### Docstrings
- Use triple quotes for all multi-line strings
- Use Google-style docstrings for public functions
```python
def calcular_score(titulo: str, descripcion: str = "") -> int:
    """Calculate job relevance score based on title and description.

    Args:
        titulo: Job title text.
        descripcion: Job description text.

    Returns:
        Score from 0-100 where higher is more relevant.
    """
```

### Error Handling
- Catch specific exceptions when possible
- Use try/except blocks with meaningful error messages
```python
try:
    df = scrape_jobs(...)
except Exception as e:
    print(f"Error scraping jobs: {e}")
```

### DataFrames (pandas)
- Use method chaining when possible
- Use `isinstance(df, pd.DataFrame)` to check before operations
```python
if isinstance(df, pd.DataFrame) and not df.empty:
    df["search_term"] = term
    df = df.drop_duplicates(subset=["job_url"], keep="first")
```

### Functions
- Keep functions focused and small (<50 lines ideal)
- Use underscore prefix for "private" module functions: `_make_session()`
- Return early to reduce nesting

### File Organization
```
jobs/
├── main.py           # Entry point with main()
├── src/
│   ├── __init__.py
│   ├── models.py     # Data classes, types
│   ├── scraping.py   # Job scraping logic
│   ├── scoring.py    # Scoring/ranking logic
│   └── utils.py      # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py
│   └── test_scraping.py
└── data/             # Output CSVs
```

### CSV Output
- Use UTF-8-BOM encoding for Excel compatibility: `encoding="utf-8-sig"`
- Include timestamp in filenames: `comparativa_mercado_YYYYMMDD_HHMM.csv`

---

## Testing Guidelines
- Use `pytest` for all tests
- Use `pytest.fixture` for shared setup
- Name test files: `test_<module>.py`
- Name test functions: `test_<function_name>_<scenario>()`

## Common Patterns

### Score Calculation Pattern
```python
def calcular_score(titulo: str, descripcion: str = "") -> int:
    texto = f"{titulo} {descripcion}".lower()
    if any(exc in texto for exc in EXCLUSION_WORDS):
        return 0
    score = 10
    for tech, weight in TECH_WEIGHTS.items():
        if tech in texto:
            score += weight
    return max(0, min(score, 100))
```

### Safe DataFrame Access
```python
if isinstance(df, pd.DataFrame) and not df.empty:
    df["new_column"] = df["existing_column"].apply(some_func)
```

### Session with Random User-Agent
```python
def _make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    })
    return s
```
