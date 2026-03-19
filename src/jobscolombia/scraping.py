import time

import nest_asyncio
import pandas as pd
from jobspy import scrape_jobs

from jobscolombia.config import SEARCH_TERMS
from jobscolombia.scoring import calcular_score, clasificar_score, identificar_stack_principal

nest_asyncio.apply()


def scrape_all_jobs(results_wanted: int = 20, delay: float = 3.0) -> pd.DataFrame | None:
    """Scrape jobs from LinkedIn and Indeed for all search terms.

    Args:
        results_wanted: Number of results per search term.
        delay: Seconds to wait between requests.

    Returns:
        Combined DataFrame with all jobs, or None if no results.
    """
    all_jobs_list = []

    for term in SEARCH_TERMS:
        print(f"   Buscando: '{term}'")
        try:
            df = scrape_jobs(
                site_name=["linkedin", "indeed"],
                search_term=term,
                location="Colombia",
                results_wanted=results_wanted,
            )

            if isinstance(df, pd.DataFrame) and not df.empty:
                df["search_term"] = term
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
                all_jobs_list.append(df)
                print(f"      {len(df)} resultados extraídos")
            else:
                print("      0 resultados encontrados")
        except Exception as e:
            print(f"      Error: {e}")
        time.sleep(delay)

    valid_dfs = [df for df in all_jobs_list if isinstance(df, pd.DataFrame) and not df.empty]
    if not valid_dfs:
        return None

    all_jobs = pd.concat(valid_dfs, ignore_index=True)
    all_jobs = all_jobs.drop_duplicates(subset=["job_url"], keep="first")
    all_jobs = all_jobs[all_jobs["score"] > 0]
    all_jobs = all_jobs.sort_values("score", ascending=False)

    return all_jobs
