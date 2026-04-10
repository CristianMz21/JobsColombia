from datetime import datetime


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
