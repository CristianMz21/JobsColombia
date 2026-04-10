#!/usr/bin/env python3
"""
Deep Analysis of JobsColombia Scraping Results

This script analyzes the scraped job vacancies to generate comprehensive
statistics, visualizations, and recommendations.
"""

import os
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

# Configuration
CSV_FILE = "comparativa_mercado_20260410_1731.csv"
OUTPUT_DIR = Path("analisis_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    """Load and validate the scraped data."""
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} job listings")
    return df


def calculate_basic_stats(df: pd.DataFrame) -> dict:
    """Calculate basic score statistics."""
    stats = {
        "total": len(df),
        "mean_score": df["score"].mean(),
        "median_score": df["score"].median(),
        "std_score": df["score"].std(),
        "min_score": df["score"].min(),
        "max_score": df["score"].max(),
        "q25": df["score"].quantile(0.25),
        "q75": df["score"].quantile(0.75),
    }
    return stats


def analyze_by_stack(df: pd.DataFrame) -> pd.Series:
    """Analyze distribution by tech stack."""
    return df["stack_principal"].value_counts()


def analyze_by_portal(df: pd.DataFrame) -> pd.Series:
    """Analyze distribution by job portal."""
    return df["site"].value_counts()


def analyze_by_clasificacion(df: pd.DataFrame) -> pd.Series:
    """Analyze distribution by quality classification."""
    order = ["Excelente", "Buena", "Regular", "Descartada"]
    return df["clasificacion"].value_counts().reindex(order, fill_value=0)


def analyze_by_location(df: pd.DataFrame) -> pd.Series:
    """Analyze job distribution by location."""
    return df["location"].value_counts().head(15)


def analyze_companies(df: pd.DataFrame) -> pd.Series:
    """Analyze top companies by job count."""
    return df["company"].value_counts().head(20)


def analyze_search_terms(df: pd.DataFrame) -> pd.Series:
    """Analyze search terms used."""
    return df["search_term"].value_counts()


def analyze_technologies(df: pd.DataFrame) -> Counter:
    """Analyze detected technologies."""
    all_techs: list[str] = []
    for techs_str in df["detected_technologies"].dropna():
        if techs_str:
            all_techs.extend([t.strip() for t in str(techs_str).split(",")])
    return Counter(all_techs)


def analyze_by_portal_and_stack(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-analysis: portal vs stack."""
    return pd.crosstab(df["site"], df["stack_principal"])


def analyze_remote_jobs(df: pd.DataFrame) -> dict:
    """Analyze remote/hybrid job distribution."""
    remote_keywords = ["remoto", "remote", "home office", "híbrido", "hybrid"]
    df["is_remote"] = df["location"].str.lower().str.contains("|".join(remote_keywords), na=False)
    return {
        "remote_count": df["is_remote"].sum(),
        "remote_pct": round(df["is_remote"].mean() * 100, 1),
        "on_site_count": len(df) - df["is_remote"].sum(),
    }


def analyze_scores_by_stack(df: pd.DataFrame) -> pd.DataFrame:
    """Average scores by tech stack."""
    return df.groupby("stack_principal")["score"].agg(["mean", "median", "count"]).round(1)


def analyze_scores_by_portal(df: pd.DataFrame) -> pd.DataFrame:
    """Average scores by portal."""
    return df.groupby("site")["score"].agg(["mean", "median", "count"]).round(1)


def generate_recommendations(df: pd.DataFrame, stats: dict, stack_counts: pd.Series, portal_counts: pd.Series) -> list[str]:
    """Generate personalized recommendations based on analysis."""
    recommendations = []

    # High-demand stacks
    top_stacks = stack_counts.head(3).index.tolist()
    recommendations.append(
        f"**Alta Demanda**: Los stacks más solicitados son {', '.join(top_stacks)}. "
        f"Considera enfocar tu búsqueda en estas tecnologías."
    )

    # Top portals
    top_portals = portal_counts.head(2).index.tolist()
    recommendations.append(
        f"**Portales Principales**: {top_portals[0]} y {top_portals[1]} lideran en oferta. "
        f"Prioriza在这些平台上找工作."
    )

    # Remote opportunities
    remote_data = analyze_remote_jobs(df)
    if remote_data["remote_pct"] > 30:
        recommendations.append(
            f"**Modalidad Remota**: {remote_data['remote_pct']}% de ofertas son remotas. "
            f"Excelente opción si buscas flexibilidad geográfica."
        )

    # Score insights
    if stats["mean_score"] < 40:
        recommendations.append(
            "**Oportunidades de Alto Score**: La mayoría de ofertas tienen scores por debajo de 50. "
            "Refina tus términos de búsqueda para encontrar ofertas más relevantes."
        )
    else:
        recommendations.append(
            "**Mercado Competitivo**: El score promedio es alto. Destácate enfatizando "
            "tus certificaciones y experiencia en tecnologías clave."
        )

    # Geographic insights
    top_city = df["location"].value_counts().index[0] if len(df["location"].value_counts()) > 0 else "N/A"
    recommendations.append(
        f"**Ubicación**: {top_city} tiene la mayor concentración de ofertas tech. "
        "Considera oportunidades en esta ciudad o busca opciones remotas."
    )

    return recommendations


def generate_markdown_report(df: pd.DataFrame) -> str:
    """Generate comprehensive markdown report."""
    stats = calculate_basic_stats(df)
    stack_counts = analyze_by_stack(df)
    portal_counts = analyze_by_portal(df)
    clasificacion_counts = analyze_by_clasificacion(df)
    location_counts = analyze_by_location(df)
    company_counts = analyze_companies(df)
    search_term_counts = analyze_search_terms(df)
    tech_counts = analyze_technologies(df)
    portal_stack_crosstab = analyze_by_portal_and_stack(df)
    remote_data = analyze_remote_jobs(df)
    scores_by_stack = analyze_scores_by_stack(df)
    scores_by_portal = analyze_scores_by_portal(df)
    recommendations = generate_recommendations(df, stats, stack_counts, portal_counts)

    report = f"""# Análisis Profundo: Mercado Tech Colombia 2026

**Fecha de scrapeo**: 10 de abril de 2026
**Total de ofertas analizadas**: {stats['total']}

---

## Resumen Ejecutivo

El scraping de portales de empleo colombianos reveló **{stats['total']} ofertas de empleo** relevantes para el sector tech. El score promedio es de **{stats['mean_score']:.1f}/100**, con una mediana de **{stats['median_score']:.1f}**. El mercado muestra una distribución interesante: la mayoría de ofertas caen en las categorías **Regular** y **Buena**, con pocas oportunidades clasificadas como **Excelente**.

---

## 1. Estadísticas Descriptivas de Scores

| Métrica | Valor |
|---------|-------|
| Total de ofertas | {stats['total']} |
| Score promedio | {stats['mean_score']:.1f} |
| Mediana | {stats['median_score']:.1f} |
| Desviación estándar | {stats['std_score']:.1f} |
| Score mínimo | {stats['min_score']} |
| Score máximo | {stats['max_score']} |
| Percentil 25% | {stats['q25']:.1f} |
| Percentil 75% | {stats['q75']:.1f} |

---

## 2. Distribución por Stack Tecnológico

{stack_counts.to_markdown()}

**Insight**: El mercado tech colombiano está dominado por **C#/.NET** y **Java/Spring**, seguidos por **Python/Django**. Esto refleja la preferencia de empresas colombianas por tecnologías empresariales maduras.

---

## 3. Distribución por Portal

{portal_counts.to_markdown()}

**Insight**: **LinkedIn** es el portal dominante con el {portal_counts.iloc[0]/stats['total']*100:.1f}% de las ofertas, seguido por **computrabajo.com**. Los portales colombianos especializados (elempleo, mitrabajo) tienen menor representación en este scrapeo.

---

## 4. Análisis Geográfico

### Top 15 Ciudades con Más Ofertas

{location_counts.to_markdown()}

**Insight**: **Bogotá** lidera ampliamente como hub tech, seguida por **Medellín**. Las ciudades principales concentran la mayor parte de las ofertas, pero hay oportunidades distribuidas en todo el país.

### Modalidad de Trabajo

| Métrica | Valor |
|---------|-------|
| Ofertas remotas | {remote_data['remote_count']} ({remote_data['remote_pct']}%) |
| Ofertas presenciales/híbridas | {remote_data['on_site_count']} ({100-remote_data['remote_pct']}%) |

---

## 5. Análisis de Tecnologías Detectadas

### Top 20 Tecnologías Más Solicitadas

| Tecnología | Frecuencia |
|------------|------------|
"""
    for tech, count in tech_counts.most_common(20):
        report += f"| {tech} | {count} |\n"

    report += f"""
**Insight**: Las tecnologías más demandadas reflejan un mercado orientado a **desarrollo backend empresarial** con fuerte presencia de .NET, Java y Spring. Python se posiciona fuertemente en roles de data/AI.

---

## 6. Clasificación de Calidad

{clasificacion_counts.to_markdown()}

| Clasificación | Rango de Score | Descripción |
|--------------|----------------|-------------|
| Excelente | ≥70 | Ofertas altamente relevantes |
| Buena | 45-69 | Buenas oportunidades |
| Regular | 20-44 | Ofertas aceptables pero no óptimas |
| Descartada | <20 | No recomendadas |

---

## 7. Análisis por Empresa

### Top 20 Empresas con Más Ofertas

{company_counts.to_markdown()}

---

## 8. Términos de Búsqueda Utilizados

{search_term_counts.to_markdown()}

---

## 9. Scores Promedio por Stack

{scores_by_stack.to_markdown()}

---

## 10. Scores Promedio por Portal

{scores_by_portal.to_markdown()}

---

## 11. Matriz: Portal vs Stack

{portal_stack_crosstab.to_markdown()}

---

## 12. Recomendaciones Personalizadas

"""
    for i, rec in enumerate(recommendations, 1):
        report += f"{i}. {rec}\n\n"

    report += f"""
---

## 13. Hallazgos Clave

1. **Mercado Backend-Dominant**: La mayoría de ofertas son para roles backend (.NET, Java, Python), con menor demanda de frontend puro.

2. **Concentración Geográfica**: Bogotá y Medellín acaparan el {((location_counts.iloc[0] + location_counts.iloc[1])/stats['total']*100):.1f}% de las ofertas.

3. **Portal LinkedIn**: Domina significativamente la oferta laboral tech en Colombia.

4. **Remoto en Crecimiento**: {remote_data['remote_pct']}% de ofertas son remotas, facilitando la búsqueda sin límite geográfico.

5. **Score Promedio Bajo**: La mediana de {stats['median_score']:.1f} indica que muchas ofertas no son óptima mente relevantes para perfiles tech especializados.

---

*Reporte generado automáticamente por JobsColombia Analytics*
*Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return report


def main() -> None:
    """Main execution function."""
    print("=" * 60)
    print("ANALISIS DE RESULTADOS - JobsColombia")
    print("=" * 60)

    # Load data
    print("\n[1/6] Cargando datos...")
    df = load_data()

    # Generate statistics
    print("[2/6] Calculando estadísticas...")
    stats = calculate_basic_stats(df)

    print("\n--- Estadísticas Básicas ---")
    print(f"Total de ofertas: {stats['total']}")
    print(f"Score promedio: {stats['mean_score']:.1f}")
    print(f"Mediana: {stats['median_score']:.1f}")
    print(f"Rango: {stats['min_score']} - {stats['max_score']}")

    # Distribution analysis
    print("\n[3/6] Analizando distribuciones...")

    print("\n--- Por Stack ---")
    print(analyze_by_stack(df).to_string())

    print("\n--- Por Portal ---")
    print(analyze_by_portal(df).to_string())

    print("\n--- Por Clasificación ---")
    print(analyze_by_clasificacion(df).to_string())

    # Technologies
    print("\n[4/6] Analizando tecnologías...")
    tech_counts = analyze_technologies(df)
    print("\n--- Top 10 Tecnologías ---")
    for tech, count in tech_counts.most_common(10):
        print(f"  {tech}: {count}")

    # Remote jobs
    print("\n[5/6] Analizando modalidad remota...")
    remote_data = analyze_remote_jobs(df)
    print(f"Remotas: {remote_data['remote_count']} ({remote_data['remote_pct']}%)")

    # Generate report
    print("\n[6/6] Generando reporte markdown...")
    report = generate_markdown_report(df)

    output_path = OUTPUT_DIR / "ANALISIS.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✓ Reporte guardado en: {output_path}")

    # Also save summary stats to JSON
    import json
    stats_output = OUTPUT_DIR / "estadisticas.json"
    with open(stats_output, "w", encoding="utf-8") as f:
        json.dump({
            "total": int(stats["total"]),
            "mean_score": round(stats["mean_score"], 2),
            "median_score": round(stats["median_score"], 2),
            "stack_distribution": analyze_by_stack(df).to_dict(),
            "portal_distribution": analyze_by_portal(df).to_dict(),
            "clasificacion_distribution": analyze_by_clasificacion(df).to_dict(),
            "top_technologies": dict(tech_counts.most_common(20)),
            "remote_pct": remote_data["remote_pct"],
        }, f, ensure_ascii=False, indent=2)

    print(f"✓ Estadísticas guardadas en: {stats_output}")

    print("\n" + "=" * 60)
    print("ANÁLISIS COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
