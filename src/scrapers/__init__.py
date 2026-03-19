"""
Scrapers module for TechJobs_Scraper_Colombia.

This module contains all spider implementations for scraping job portals:
- BaseJobSpider: Abstract base class with anti-detection measures
- ElEmpleoSpider: Spider for elempleo.com
- ComputrabajoSpider: Spider for computrabajo.com
- MiTrabajoSpider: Spider for mitrabajo.co
"""

from src.scrapers.base import BaseJobSpider
from src.scrapers.computrabajo import ComputrabajoSpider
from src.scrapers.elempleo import ElEmpleoSpider
from src.scrapers.mitrabajo import MiTrabajoSpider

__all__ = [
    "BaseJobSpider",
    "ElEmpleoSpider",
    "ComputrabajoSpider",
    "MiTrabajoSpider",
]
