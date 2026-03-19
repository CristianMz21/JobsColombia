"""JobsColombia - Tech job scraper for Colombia."""

__version__ = "0.1.0"
__author__ = "TechJobs Colombia"
__license__ = "MIT"

from jobscolombia.scraping import scrape_all_jobs
from jobscolombia.scoring import calcular_score, clasificar_score

__all__ = [
    "scrape_all_jobs",
    "calcular_score",
    "clasificar_score",
]
