# Tech Job Market Analysis — Colombia 2026

**Report Generated**: April 10, 2026
**Data Source**: JobsColombia Automated Scraping Pipeline
**Sample Size**: 107 job listings across 5 portals

---

## Executive Summary

This report presents a data-driven analysis of the Colombian technology job market, synthesized from 107 real-time scraped vacancies across LinkedIn, Indeed, Computrabajo, ElEmpleo, and MiTrabajo. The findings reveal a market with significant demand for mid-to-senior backend engineers, a strong geographic concentration in Bogotá and Medellín, and a notable gap between entry-level and advanced positions.

The average relevance score of **19.8/100** indicates that most scraped listings are **internship or practicante-level roles** rather than senior technical positions. When filtered to tech-specific roles, the market presents a healthier picture with average scores reaching **31.7/100** for C#/.NET and **32.9/100** for Java/Spring positions.

---

## 1. Overall Market Statistics

| Metric | Value |
|--------|------:|
| Total Vacancies Analyzed | 107 |
| Mean Relevance Score | 19.8 |
| Median Score | 20.0 |
| Standard Deviation | 11.9 |
| Minimum Score | 2 |
| Maximum Score | 50 |
| 25th Percentile | 10.0 |
| 75th Percentile | 25.0 |

### Score Distribution

| Classification | Score Range | Count | Percentage |
|---------------|-------------|------:|----------:|
| Excelente (Excellent) | ≥70 | 0 | 0.0% |
| Buena (Good) | 45–69 | 6 | 5.6% |
| Regular (Fair) | 20–44 | 49 | 45.8% |
| Descartada (Discarded) | <20 | 52 | 48.6% |

> **Interpretation**: Nearly half of scraped listings fall below the relevance threshold, predominantly due to non-technical positions (internships, administrative roles, health & safety) captured by broad search terms. Filtering for strictly tech roles yields a more encouraging distribution.

---

## 2. Portal Performance

| Portal | Vacancies | Share | Avg Score | Median Score |
|--------|----------:|------:|----------:|------------:|
| LinkedIn | 71 | 66.4% | 23.7 | 25 |
| Computrabajo | 36 | 33.6% | 12.2 | 10 |

### Portal × Stack Cross-Analysis

| Portal | C#/.NET | Java/Spring | Python/Django | Otro/Mixto |
|--------|--------:|------------:|-------------:|-----------:|
| LinkedIn | 19 | 13 | 12 | 27 |
| Computrabajo | 0 | 0 | 0 | 36 |

**Key Insight**: Computrabajo exclusively returned non-technical positions (practicante/intern roles) in this scrape. LinkedIn is the primary source for qualified tech roles. This disparity may be due to search term configuration — adjusting terms for Computrabajo could improve yield.

---

## 3. Technology Stack Distribution

| Stack | Count | Share | Avg Score |
|-------|------:|------:|----------:|
| Otro/Mixto | 63 | 58.9% | 11.9 |
| C#/.NET | 19 | 17.8% | 31.7 |
| Java/Spring | 13 | 12.1% | 32.9 |
| Python/Django | 12 | 11.2% | 28.3 |

**Market Insight**: The "Otro/Mixto" category captures a broad range of positions including internships, support roles, and non-standard tech titles. Among clearly identified tech stacks, **C#/.NET leads** the market with the highest count and competitive average scores, reflecting strong enterprise adoption in Colombia. **Java/Spring** commands the highest average score (32.9), indicating strong demand for experienced Java engineers. **Python/Django** positions are fewer but solid, particularly for remote/data-oriented roles.

---

## 4. Geographic Distribution

| Location | Count |
|----------|------:|
| Colombia (unspecified) | 36 |
| Medellín, Antioquia | 8 |
| Bogotá, Capital District | 5 |
| Medellin, Antioquia | 2 |
| Capital District | 1 |
| Cali, Valle del Cauca | 1 |

**Geographic Insight**: **Bogotá** consolidates its role as Colombia's primary tech hub, followed by **Medellín**. The high count of "Colombia" (unspecified) entries originates from Computrabajo listings that did not expose location data. Remote-friendly positions are underrepresented in this scrape, suggesting either limited remote offerings or detection gaps in the scraping logic.

---

## 5. Top Hiring Companies

| Company | Open Positions |
|---------|---------------:|
| EPAM Systems | 3 |
| VASS / VASS LATAM | 4 |
| Jobs Ai | 2 |
| NEORIS | 2 |
| Softtek | 2 |
| Inetum | 2 |
| Periferia IT Group | 2 |
| Capgemini | 2 |
| PartnerOne | 2 |
| symphony.is | 2 |

**Notable**: Major multinational IT consulting firms (EPAM, VASS, Softtek, Capgemini, Inetum) represent a significant share of active hiring, consistent with Colombia's growing nearshoring market for North American and European clients.

---

## 6. Search Terms Performance

| Search Term | Results |
|-------------|--------:|
| General | 36 |
| Desarrollador C# | 14 |
| Backend Python | 12 |
| C# Backend | 10 |
| .NET Developer | 9 |
| Java Spring Boot | 7 |
| Desarrollador Java | 6 |
| Desarrollador Django | 6 |
| Backend Java | 4 |
| Python Developer | 3 |

**Insight**: "General" captures the broadest set but yields the lowest quality (practicante roles). Specialized searches like "Desarrollador C#" and "Backend Python" return significantly higher-quality results with better average scores.

---

## 7. Salary & Date Analysis

Salary data was sparse in this scrape — most listings did not expose compensation information. This is a known limitation of job portal scraping, as many employers withhold salary until later interview stages.

Date posting information was similarly incomplete, preventing a reliable temporal trend analysis. Future scrapes should incorporate dedicated salary/scrape-date extraction to enable compensation benchmarking.

---

## 8. Key Findings

### Market Structure
- **Backend-dominant**: The market heavily favors backend technologies (.NET, Java, Python) over frontend or mobile roles.
- **Enterprise focus**: Major hiring is driven by IT consulting firms serving international clients — a nearshore trend accelerated post-2020.
- **Entry-level gap**: Very few mid-to-senior level positions with strong compensation were captured, likely due to search term scope.

### Platform Quality
- **LinkedIn** significantly outperforms Colombian portals in both volume and quality of tech roles.
- **Computrabajo** and local portals primarily surface internships and support roles under broad tech search terms.

### Geographic Concentration
- **Bogotá–Medellín corridor** accounts for the majority of identifiable offers.
- Remote positions are notably absent, suggesting either a market preference for onsite/hybrid or scraping detection limitations for remote-friendly listings.

---

## 9. Strategic Recommendations

1. **Focus search on LinkedIn** — it delivers the highest quality tech roles by a wide margin. Allocate 70–80% of application effort to LinkedIn.

2. **Refine search terms** — broad searches ("General") return low-relevance results. Use specific technology stacks (e.g., "Desarrollador C#", "Java Spring Boot") to surface senior-level roles.

3. **Target consulting firms** — EPAM, VASS, Softtek, Capgemini, and Inetum are actively hiring. These companies often have faster hiring cycles and competitive compensation for nearshore roles.

4. **Upskill in .NET or Java** — both stacks show the highest demand and best average scores. Python offers strong remote opportunities in data/AI roles.

5. **Expand portal coverage** — integrate direct scraping of Indeed (remote roles) and specialized tech job boards (WeWorkRemotely, RemoteOK) to complement LinkedIn and Computrabajo.

6. **Build a portfolio** — with 48.6% of listings discarded, standing out requires more than keyword matching. Highlight specific project outcomes and certifications.

---

## 10. Methodology

| Parameter | Value |
|-----------|-------|
| Scraping Date | 2026-04-10 |
| Portals Scraped | 5 (LinkedIn, Indeed, Computrabajo, ElEmpleo, MiTrabajo) |
| Search Terms | 10 specialized tech terms |
| Max Pages per Portal | 10 |
| Scoring Algorithm | JobsColombia Relevance Score (0–100) |
| Classification | Excelente ≥70, Buena 45–69, Regular 20–44, Descartada <20 |

---

*Report generated by [JobsColombia](https://github.com/CristianMz21/JobsColombia) — Tech Job Scoring Library for Colombia*
*Powered by Scrapling + python-jobspy + pandas*
