"""
TechJobs_Scraper_Colombia - Main Entry Point.

This module orchestrates job scraping from multiple portals:
- LinkedIn & Indeed (via JobSpy)
- elempleo.com (via ElEmpleoSpider)
- computrabajo.com (via ComputrabajoSpider)
- mitrabajo.co (via MiTrabajoSpider)

All results are unified into a single DataFrame, scored, and exported to CSV.
"""

import time
from datetime import datetime
from typing import Any

import nest_asyncio
import pandas as pd
from jobspy import scrape_jobs

from src.config import CSV_COLUMNS, EXPORT_ENCODING, SEARCH_TERMS
from src.logger import logger
from src.scoring import (
    calcular_score,
    clasificar_score,
    extract_technologies,
    identificar_stack_principal,
)
from src.utils import generar_nombre_csv

nest_asyncio.apply()


def scrape_jobspy_jobs(results_wanted: int = 15, delay: float = 3.0) -> list[pd.DataFrame]:
    """Scrape jobs from LinkedIn and Indeed using JobSpy.

    Args:
        results_wanted: Number of results per search term.
        delay: Seconds to wait between requests.

    Returns:
        List of DataFrames with job listings.
    """
    all_jobs: list[pd.DataFrame] = []
    logger.info("Extrayendo empleos de LinkedIn e Indeed...")

    for term in SEARCH_TERMS:
        logger.info(f"Buscando: '{term}'")
        try:
            df = scrape_jobs(
                site_name=["linkedin", "indeed"],
                search_term=term,
                location="Colombia",
                results_wanted=results_wanted,
            )

            if isinstance(df, pd.DataFrame) and not df.empty:
                df["search_term"] = term
                df["site"] = df["job_url"].apply(
                    lambda url: "linkedin" if "linkedin" in str(url).lower() else "indeed"
                )
                df["full_description"] = df["description"].apply(
                    lambda d: str(d) if pd.notna(d) else ""
                )
                df["detected_technologies"] = df["full_description"].apply(
                    lambda d: ", ".join(extract_technologies(d))
                )
                df["score"] = df.apply(
                    lambda r: calcular_score(
                        str(r.get("title", "")),
                        str(r.get("description", "")),
                        str(r.get("location", "")),
                        str(r.get("company", "")),
                    ),
                    axis=1,
                )
                df["stack_principal"] = df.apply(
                    lambda r: identificar_stack_principal(
                        f"{str(r.get('title', ''))} {str(r.get('description', ''))}"
                    ),
                    axis=1,
                )
                df["clasificacion"] = df["score"].apply(clasificar_score)
                df["date_posted"] = df.get("date_posted", "")
                df["salary"] = df.get("salary", "")
                df["description"] = ""
                all_jobs.append(df)
                logger.info(f"{len(df)} resultados extraídos de LinkedIn/Indeed para '{term}'")
            else:
                logger.warning(f"0 resultados encontrados para '{term}'")
        except Exception as e:
            logger.error(f"Error extrayendo de LinkedIn/Indeed: {e}")
        time.sleep(delay)

    return all_jobs


def scrape_portal_jobs(
    spider_class: Any,
    name: str,
    max_pages: int = 3,
) -> list[dict[str, Any]]:
    """Scrape jobs from a portal using Scrapling spiders.

    Args:
        spider_class: Spider class to instantiate.
        name: Name of the portal for logging.
        max_pages: Maximum pages to scrape per spider.

    Returns:
        List of job dictionaries.
    """
    logger.info(f"Extrayendo empleos de {name}...")
    jobs: list[dict[str, Any]] = []

    try:
        spider = spider_class()
        spider.max_pages = max_pages
        result = spider.start()

        for item in result.items:
            jobs.append(item)

        logger.info(f"{len(jobs)} empleos extraídos de {name}")
    except Exception as e:
        logger.error(f"Error scraping {name}: {e}")

    return jobs


def scrape_all_jobs_async(max_pages: int = 3) -> pd.DataFrame | None:
    """Scrape jobs from all portals in parallel.

    This function orchestrates scraping from all configured job portals,
    combines the results, and returns a unified DataFrame.

    Args:
        max_pages: Maximum pages to scrape per portal spider.

    Returns:
        Combined DataFrame with all jobs, or None if no results.
    """
    from src.scrapers.computrabajo import ComputrabajoSpider
    from src.scrapers.elempleo import ElEmpleoSpider
    from src.scrapers.mitrabajo import MiTrabajoSpider

    logger.info("=" * 60)
    logger.info("INICIANDO WEB SCRAPING MULTI-PORTAL")
    logger.info("=" * 60)

    jobspy_dfs = scrape_jobspy_jobs(results_wanted=15)

    portal_spiders = [
        (ElEmpleoSpider, "elempleo.com"),
        (ComputrabajoSpider, "computrabajo.com"),
        (MiTrabajoSpider, "mitrabajo.co"),
    ]

    all_portal_jobs: list[dict[str, Any]] = []
    for spider_class, name in portal_spiders:
        try:
            jobs = scrape_portal_jobs(spider_class, name, max_pages=max_pages)
            all_portal_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"Error with {name}: {e}")

    all_dfs: list[pd.DataFrame] = jobspy_dfs.copy()

    if all_portal_jobs:
        portal_df = pd.DataFrame(all_portal_jobs)
        if not portal_df.empty:
            all_dfs.append(portal_df)

    if not all_dfs:
        return None

    combined = pd.concat(all_dfs, ignore_index=True)

    if "title" in combined.columns and "company" in combined.columns:
        combined["clave_deduplicacion"] = (
            combined["title"].str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
            + "|"
            + combined["company"].str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
        )
        combined = combined.drop_duplicates(subset=["clave_deduplicacion"], keep="first")
        combined = combined.drop(columns=["clave_deduplicacion"])
    elif "job_url" in combined.columns:
        combined = combined.drop_duplicates(subset=["job_url"], keep="first")

    combined = combined[combined["score"] > 0]
    combined = combined.sort_values("score", ascending=False)

    return combined


def print_statistics(df: pd.DataFrame) -> None:
    """Print job market statistics.

    Args:
        df: DataFrame containing job listings.
    """
    logger.info("=" * 60)
    logger.info("ESTADÍSTICAS DEL MERCADO LABORAL EN COLOMBIA")
    logger.info("=" * 60)
    logger.info(f"Total vacantes útiles encontradas: {len(df)}")

    logger.info("EMPLEABILIDAD POR TECNOLOGÍA:")
    if "stack_principal" in df.columns:
        stats = df["stack_principal"].value_counts()
        for stack, count in stats.items():
            porcentaje = (count / len(df)) * 100
            logger.info(f"  - {stack}: {count} ofertas ({porcentaje:.1f}%)")

    logger.info("DISTRIBUCIÓN POR PORTAL:")
    if "site" in df.columns:
        site_stats = df["site"].value_counts()
        for site, count in site_stats.items():
            porcentaje = (count / len(df)) * 100
            logger.info(f"  - {site}: {count} ofertas ({porcentaje:.1f}%)")

    logger.info("CALIDAD DE LAS OFERTAS (Según tu perfil):")
    if "clasificacion" in df.columns:
        for label in ["Excelente", "Buena", "Regular", "Descartada"]:
            count = len(df[df["clasificacion"] == label])
            logger.info(f"  {label}: {count}")


def export_to_csv(df: pd.DataFrame, filename: str | None = None) -> str:
    """Export DataFrame to CSV with specified columns.

    Args:
        df: DataFrame to export.
        filename: Optional custom filename.

    Returns:
        Path to the exported CSV file.
    """
    if filename is None:
        filename = generar_nombre_csv()

    cols = [c for c in CSV_COLUMNS if c in df.columns]
    if not cols:
        cols = list(df.columns)

    df[cols].to_csv(filename, index=False, encoding=EXPORT_ENCODING)
    return filename


def main() -> None:
    """Main entry point for the job scraper."""
    logger.info("=" * 60)
    logger.info("BUSQUEDA DE EMPLEOS TECH - COMPARATIVA DE MERCADO")
    logger.info("=" * 60)
    logger.info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Portales: LinkedIn, Indeed, elempleo.com, computrabajo.com, mitrabajo.co")
    logger.info(f"Términos de búsqueda: {', '.join(SEARCH_TERMS[:3])}...")

    start_time = time.time()

    all_jobs = scrape_all_jobs_async(max_pages=3)

    elapsed = time.time() - start_time

    if all_jobs is None or all_jobs.empty:
        logger.warning("No se encontraron vacantes.")
        return

    print_statistics(all_jobs)

    filename = export_to_csv(all_jobs)
    logger.info(f"Guardado: '{filename}'")
    logger.info(f"Tiempo total: {elapsed:.1f} segundos")


if __name__ == "__main__":
    main()
