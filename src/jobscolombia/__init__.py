"""JobsColombia - Tech job scoring and utilities for Colombia."""

__version__ = "0.2.0"
__author__ = "TechJobs Colombia"
__license__ = "MIT"

from jobscolombia.scoring import calcular_score, clasificar_score, identificar_stack_principal

__all__ = [
    "calcular_score",
    "clasificar_score",
    "identificar_stack_principal",
]
