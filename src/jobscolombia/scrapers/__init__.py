"""
Scrapers module for TechJobs_Scraper_Colombia.

This module contains all spider implementations for scraping job portals:
- BaseJobSpider: Abstract base class with anti-detection measures
- ElEmpleoSpider: Spider for elempleo.com
- ComputrabajoSpider: Spider for computrabajo.com
- MiTrabajoSpider: Spider for mitrabajo.co
"""

from jobscolombia.scrapers.base import BaseJobSpider
from jobscolombia.scrapers.computrabajo import ComputrabajoSpider
from jobscolombia.scrapers.elempleo import ElEmpleoSpider
from jobscolombia.scrapers.mitrabajo import MiTrabajoSpider

__all__ = [
    "BaseJobSpider",
    "ElEmpleoSpider",
    "ComputrabajoSpider",
    "MiTrabajoSpider",
]
