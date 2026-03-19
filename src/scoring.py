"""
Scoring module for TechJobs_Scraper_Colombia.

This module provides the logic for calculating job relevance scores based on:
- Technology stack matches
- Seniority level preferences
- Work modality preferences
- Exclusion of irrelevant job postings
- Dynamic technology extraction from job descriptions
"""

import re
from typing import Final

from src.config import BLACKLIST_COMPANIES, SCORING_CONFIG

TECHNOLOGIES: Final[list[tuple[str, re.Pattern[str]]]] = [
    (tech, re.compile(rf"\b{re.escape(tech)}\b", re.IGNORECASE))
    for tech in [
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "k8s",
        "jenkins",
        "gitlab",
        "github",
        "bitbucket",
        "jira",
        "confluence",
        "terraform",
        "ansible",
        "chef",
        "puppet",
        "prometheus",
        "grafana",
        "elk",
        "elasticsearch",
        "kafka",
        "rabbitmq",
        "redis",
        "mongodb",
        "postgresql",
        "mysql",
        "oracle",
        "sql server",
        "mariadb",
        "firebase",
        "dynamodb",
        "s3",
        "ec2",
        "lambda",
        "python",
        "django",
        "fastapi",
        "flask",
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "java",
        "spring",
        "spring boot",
        "springboot",
        "hibernate",
        "jpa",
        "maven",
        "gradle",
        "kotlin",
        "scala",
        "c#",
        ".net",
        "asp.net",
        "net core",
        "netcore",
        "entity framework",
        "linq",
        "javascript",
        "typescript",
        "react",
        "reactjs",
        "angular",
        "angularjs",
        "vue",
        "vuejs",
        "next.js",
        "nextjs",
        "node",
        "nodejs",
        "express",
        "jquery",
        "html",
        "css",
        "sass",
        "less",
        "bootstrap",
        "tailwind",
        "graphql",
        "rest",
        "restful",
        "api",
        "microservices",
        "monolithic",
        "agile",
        "scrum",
        "kanban",
        "ci/cd",
        "cicd",
        "devops",
        "git",
        "svn",
        "tfs",
        "jira",
        "uml",
        "oauth",
        "jwt",
        "ssl",
        "tls",
        "nginx",
        "apache",
        "tomcat",
        "linux",
        "unix",
        "windows server",
        "bash",
        "powershell",
        "sql",
        "nosql",
        "orm",
        "oop",
        "clean code",
        "solid",
        "tdd",
        "bdd",
        "unit tests",
        "selenium",
        "cypress",
        "playwright",
        "postman",
        "soapui",
        "jmeter",
        "load testing",
        "performance testing",
        "security testing",
        "penetration testing",
        "owasp",
        "saas",
        "paas",
        "iaas",
        "serverless",
        "container",
        "orchestration",
        "ci cd",
    ]
]


def extract_technologies(description: str) -> list[str]:
    """Extract technologies from job description using regex.

    This function searches for known technology keywords in the job
    description and returns a clean list of detected technologies.

    Args:
        description: Full job description text to analyze.

    Returns:
        List of detected technologies (deduplicated, case-preserved).
    """
    if not description:
        return []

    detected: set[str] = set()
    desc_lower = description.lower()

    for tech, pattern in TECHNOLOGIES:
        if pattern.search(desc_lower):
            detected.add(tech)

    return sorted(detected)


def calcular_score(
    titulo: str,
    descripcion: str = "",
    ubicacion: str = "",
    empresa: str = "",
) -> int:
    """Calculate job relevance score based on title, description, and location.

    This function evaluates a job posting against configured weights for
    technology stack, seniority level, and work modality. Jobs that contain
    exclusion words or lack required keywords receive a score of 0.

    Args:
        titulo: Job title text to analyze.
        descripcion: Job description text (optional).
        ubicacion: Job location text (optional).
        empresa: Company name (optional). If matches BLACKLIST_COMPANIES, score is 0.

    Returns:
        Score from 0 to 100 where:
        - 0: Job is excluded (contains exclusion words or lacks required keywords)
        - 1-19: Low relevance
        - 20-44: Medium relevance
        - 45-69: Good relevance
        - 70-100: Excellent relevance

    Example:
        >>> score = calcular_score(
        ...     "Desarrollador Python Django Senior Remoto",
        ...     "Buscamos desarrollador con 5 años de experiencia...",
        ...     "Bogotá, Colombia"
        ... )
        >>> print(f"Score: {score}")
    """
    try:
        if empresa:
            empresa_lower = empresa.lower().strip()
            if empresa_lower in [c.lower() for c in BLACKLIST_COMPANIES]:
                return 0

        # Combine all text for analysis (case-insensitive)
        texto = f"{titulo} {descripcion} {ubicacion}".lower()

        # Step 1: Check for exclusion words (immediate disqualification)
        if any(exc in texto for exc in SCORING_CONFIG.exclusion_words):
            return 0

        # Step 2: Check for required keywords (must have at least one)
        if not any(req in texto for req in SCORING_CONFIG.required_words):
            return 0

        # Step 3: Calculate base score
        score = 10  # Base score for matching required words

        # Step 4: Add points for technology matches
        for tech, weight in SCORING_CONFIG.tech_weights.items():
            if tech in texto:
                score += weight

        # Step 5: Add points for seniority preferences
        for level, weight in SCORING_CONFIG.seniority_weights.items():
            if level in texto:
                score += weight

        # Step 6: Add points for modality preferences
        for mod, weight in SCORING_CONFIG.modality_weights.items():
            if mod in texto:
                score += weight

        # Step 7: Clamp score to valid range [0, 100]
        return max(0, min(score, SCORING_CONFIG.max_score))

    except Exception as e:
        # Log error but return 0 to avoid breaking the scraping pipeline
        print(f"Error calculating score: {e}")
        return 0


def clasificar_score(score: int) -> str:
    """Classify a numeric score into a human-readable category.

    Args:
        score: Numeric score from 0 to 100.

    Returns:
        Category label:
        - "Excelente": Score >= 70 (highly relevant)
        - "Buena": Score 45-69 (good relevance)
        - "Regular": Score 20-44 (acceptable relevance)
        - "Descartada": Score < 20 (low or no relevance)

    Example:
        >>> clasificar_score(85)
        'Excelente'
        >>> clasificar_score(35)
        'Regular'
    """
    try:
        if score >= 70:
            return "Excelente"
        if score >= 45:
            return "Buena"
        if score >= SCORING_CONFIG.min_score:
            return "Regular"
        return "Descartada"
    except Exception as e:
        print(f"Error classifying score: {e}")
        return "Descartada"


def identificar_stack_principal(texto: str) -> str:
    """Identify the primary technology stack from job text.

    This function analyzes the job title and description to determine
    which technology stack is most prominent. Detection is based on
    keyword matching with priority ordering.

    Args:
        texto: Combined job title and description text.

    Returns:
        Technology stack category:
        - "Python/Django": Python, Django, FastAPI, Flask
        - "Java/Spring": Java, Spring, Spring Boot
        - "C#/.NET": C#, .NET, ASP.NET, DotNet Core
        - "Otro/Mixto": No specific stack identified

    Example:
        >>> identificar_stack_principal("Desarrollador Python Django")
        'Python/Django'
        >>> identificar_stack_principal("Java Spring Boot Microservices")
        'Java/Spring'
    """
    try:
        texto = str(texto).lower()

        # Priority order: Check most specific technologies first
        # Python stack
        if any(tech in texto for tech in ["python", "django", "fastapi", "flask"]):
            return "Python/Django"

        # Java stack
        if any(tech in texto for tech in ["java", "spring", "spring boot", "springboot"]):
            return "Java/Spring"

        # C# stack
        if any(
            tech in texto
            for tech in ["c#", ".net", "asp.net", "aspnet", "dotnet", "net core", "netcore"]
        ):
            return "C#/.NET"

        # React (frontend special case)
        if "react" in texto:
            return "React/Frontend"

        # No specific stack detected
        return "Otro/Mixto"

    except Exception as e:
        print(f"Error identifying stack: {e}")
        return "Otro/Mixto"


def calcular_score_detallado(
    titulo: str,
    descripcion: str = "",
    ubicacion: str = "",
) -> dict:
    """Calculate detailed score breakdown for debugging and analysis.

    This function provides a detailed breakdown of the score calculation,
    showing individual contributions from each category.

    Args:
        titulo: Job title text.
        descripcion: Job description text (optional).
        ubicacion: Job location text (optional).

    Returns:
        Dictionary containing:
        - total_score: Final calculated score
        - clasificacion: Human-readable category
        - stack: Identified technology stack
        - tech_matches: List of matched technologies with weights
        - seniority_match: Matched seniority level (if any)
        - modality_match: Matched modality preference (if any)
        - excluded: Boolean indicating if job was excluded

    Example:
        >>> result = calcular_score_detallado("Python Developer Senior Remote")
        >>> print(result['tech_matches'])
        [('python', 15)]
    """
    try:
        texto = f"{titulo} {descripcion} {ubicacion}".lower()

        result = {
            "total_score": 0,
            "clasificacion": "Descartada",
            "stack": "Otro/Mixto",
            "tech_matches": [],
            "seniority_match": None,
            "modality_match": None,
            "excluded": False,
        }

        # Check exclusions
        if any(exc in texto for exc in SCORING_CONFIG.exclusion_words):
            result["excluded"] = True
            return result

        # Check required words
        if not any(req in texto for req in SCORING_CONFIG.required_words):
            return result

        # Calculate tech matches
        tech_score = 0
        for tech, weight in SCORING_CONFIG.tech_weights.items():
            if tech in texto:
                result["tech_matches"].append((tech, weight))
                tech_score += weight

        # Calculate seniority match
        seniority_score = 0
        for level, weight in SCORING_CONFIG.seniority_weights.items():
            if level in texto:
                result["seniority_match"] = (level, weight)
                seniority_score += weight
                break  # Only count the first match

        # Calculate modality match
        modality_score = 0
        for mod, weight in SCORING_CONFIG.modality_weights.items():
            if mod in texto:
                result["modality_match"] = (mod, weight)
                modality_score += weight
                break  # Only count the first match

        # Calculate total
        result["total_score"] = max(
            0,
            min(
                10 + tech_score + seniority_score + modality_score,
                SCORING_CONFIG.max_score,
            ),
        )
        result["clasificacion"] = clasificar_score(result["total_score"])
        result["stack"] = identificar_stack_principal(texto)

        return result

    except Exception as e:
        print(f"Error in detailed scoring: {e}")
        return {
            "total_score": 0,
            "clasificacion": "Descartada",
            "stack": "Otro/Mixto",
            "tech_matches": [],
            "seniority_match": None,
            "modality_match": None,
            "excluded": True,
        }
