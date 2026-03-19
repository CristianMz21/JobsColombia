import random
from datetime import datetime

import requests

from src.config import USER_AGENTS


def _make_session() -> requests.Session:
    """Create a requests session with random user agent."""
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-CO,es;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    )
    return s


def generar_nombre_csv() -> str:
    """Generate timestamped CSV filename."""
    return f"comparativa_mercado_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"


def columnas_export() -> list[str]:
    """Return ordered list of columns for CSV export."""
    return [
        "stack_principal",
        "score",
        "clasificacion",
        "title",
        "company",
        "location",
        "site",
        "search_term",
        "job_url",
    ]
