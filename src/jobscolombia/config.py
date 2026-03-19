"""
Configuration module for TechJobs_Scraper_Colombia.

This module centralizes all configuration settings including:
- Search terms for job portals
- Scoring weights for job relevance
- Anti-detection settings
- Rate limiting parameters
"""

from dataclasses import dataclass, field
from typing import Final

USER_AGENTS: Final[list[str]] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

# ==============================================================================
# SEARCH TERMS CONFIGURATION
# ==============================================================================

SEARCH_TERMS: Final[list[str]] = [
    # Python/Django
    "Backend Python",
    "Desarrollador Django",
    "Python Developer",
    # Java/Spring
    "Desarrollador Java",
    "Java Spring Boot",
    "Backend Java",
    # C#/.NET
    "Desarrollador C#",
    ".NET Developer",
    "C# Backend",
]

JOB_BOARDS: Final[list[str]] = [
    "elempleo.com",
    "computrabajo.com",
    "mitrabajo.co",
]

LOCATION: Final[str] = "Colombia"

BLACKLIST_COMPANIES: Final[list[str]] = [
    "bairesdev",
    "bairesdev s.a",
    "bairesdev s.a.",
    "turing",
    "crossover",
    "topcoder",
]

# ==============================================================================
# PROXY CONFIGURATION
# ==============================================================================

PROXIES: list[str] = []


# ==============================================================================
# SCORING CONFIGURATION
# ==============================================================================


@dataclass
class ScoringConfig:
    """Configuration for job relevance scoring system.

    Attributes:
        tech_weights: Points awarded for each technology found in job posting.
        seniority_weights: Points awarded/penalized for seniority levels.
        modality_weights: Points awarded for work modality preferences.
        exclusion_words: Words that immediately discard a job posting.
        required_words: Words that must be present for a job to be considered.
    """

    tech_weights: dict[str, int] = field(
        default_factory=lambda: {
            # Python/Django stack - balanced weights
            "python": 15,
            "django": 15,
            "fastapi": 15,
            "flask": 10,
            "pandas": 5,
            "numpy": 5,
            # Java/Spring stack - balanced weights
            "java": 15,
            "spring": 15,
            "spring boot": 15,
            "springboot": 15,
            "hibernate": 8,
            "maven": 5,
            "gradle": 5,
            # C#/.NET stack - balanced weights
            "c#": 15,
            ".net": 15,
            "asp.net": 15,
            "aspnet": 15,
            "dotnet": 15,
            "net core": 15,
            "netcore": 15,
            # Frontend/Full Stack
            "react": 10,
            "angular": 10,
            "vue": 8,
            "typescript": 10,
            "javascript": 8,
            # Databases
            "sql": 6,
            "postgresql": 8,
            "mysql": 6,
            "oracle": 5,
            "mongodb": 6,
            # DevOps & Cloud
            "docker": 6,
            "kubernetes": 8,
            "aws": 5,
            "azure": 5,
            "gcp": 5,
            "jenkins": 4,
            "ci/cd": 5,
            "git": 3,
        }
    )

    seniority_weights: dict[str, int] = field(
        default_factory=lambda: {
            # Junior levels (positive points for learning opportunities)
            "junior": 10,
            "jr": 10,
            "practicante": 12,
            "aprendiz": 12,
            "trainee": 10,
            "sin experiencia": 8,
            "entry level": 8,
            # Mid levels (neutral)
            "mid": 5,
            "semi senior": 5,
            "semi-senior": 5,
            # Senior levels (penalized for market comparison)
            "senior": -5,
            "sr": -5,
            "lead": -8,
            "architect": -10,
            "manager": -12,
            "gerente": -12,
            "director": -12,
        }
    )

    modality_weights: dict[str, int] = field(
        default_factory=lambda: {
            # Remote is preferred
            "remoto": 15,
            "remote": 15,
            "trabajo remoto": 15,
            "from home": 15,
            "teletrabajo": 15,
            # Hybrid is acceptable
            "híbrido": 8,
            "hibrido": 8,
            "hybrid": 8,
            "mixto": 8,
            "presencial": 0,
        }
    )

    exclusion_words: list[str] = field(
        default_factory=lambda: [
            # Non-tech jobs that often appear in tech searches
            "enfermera",
            "enfermero",
            "conductor",
            "escolta",
            "cobranza",
            "ventas externas",
            "asesor comercial",
            "operario",
            "operaria",
            "aseo",
            "mensajero",
            "mensajera",
            "médico",
            "medico",
            "bodega",
            "vigilante",
            "auxiliar contable",
            "recepcionista",
            "cajero",
            "cajera",
            "vendedor",
            "vendedora",
            "promotor",
            "promotora",
            "auxiliar de cocina",
            "chef",
            "cocinero",
            "cocinera",
            # Completely unrelated
            "contador",
            "abogado",
            "abogada",
            "psicólogo",
            "psicologo",
        ]
    )

    required_words: list[str] = field(
        default_factory=lambda: [
            # Developer/Programming terms
            "python",
            "django",
            "java",
            "spring",
            "c#",
            ".net",
            "react",
            "backend",
            "back end",
            "full stack",
            "fullstack",
            "full-stack",
            "desarrollador",
            "desarrolladora",
            "developer",
            "programador",
            "programadora",
            "software",
            "sistemas",
            # Technical roles
            "devops",
            "ingeniero",
            "ingeniera",
            "arquitecto",
            "arquitecta",
            "adso",
            "practicante",
            "técnico",
            "tecnico",
        ]
    )

    @property
    def min_score(self) -> int:
        """Minimum score threshold for a job to be considered relevant."""
        return 20

    @property
    def max_score(self) -> int:
        """Maximum possible score (capped)."""
        return 100


# Global scoring configuration instance
SCORING_CONFIG: Final[ScoringConfig] = ScoringConfig()


# ==============================================================================
# ANTI-DETECTION CONFIGURATION
# ==============================================================================


@dataclass
class AntiDetectionConfig:
    """Configuration for anti-detection measures.

    Attributes:
        min_delay: Minimum delay between requests in seconds.
        max_delay: Maximum delay between requests in seconds.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retry attempts.
        concurrent_requests: Maximum concurrent requests allowed.
        impersonate_browser: Browser to impersonate for HTTP requests.
    """

    min_delay: float = 4.0
    max_delay: float = 8.0
    timeout: int = 30
    max_retries: int = 3
    concurrent_requests: int = 3
    impersonate_browser: str = "chrome"
    headless: bool = True
    block_webrtc: bool = True
    hide_canvas: bool = True
    solve_cloudflare: bool = True
    locale: str = "es-CO"
    timezone_id: str = "America/Bogota"


ANTIDETECTION_CONFIG: Final[AntiDetectionConfig] = AntiDetectionConfig()


# ==============================================================================
# EXPORT CONFIGURATION
# ==============================================================================

CSV_COLUMNS: Final[list[str]] = [
    "stack_principal",
    "score",
    "clasificacion",
    "title",
    "company",
    "location",
    "site",
    "search_term",
    "job_url",
    "salary",
    "date_posted",
    "description",
    "full_description",
    "detected_technologies",
]

EXPORT_ENCODING: Final[str] = "utf-8-sig"
