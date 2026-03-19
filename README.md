# TechJobs Colombia

> Web scraper profesional para ofertas de empleo tech en Colombia.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/CristianMz21/JobsColombia/actions/workflows/tests.yml/badge.svg)](https://github.com/CristianMz21/JobsColombia/actions/workflows/tests.yml)
[![Lint](https://github.com/CristianMz21/JobsColombia/actions/workflows/lint.yml/badge.svg)](https://github.com/CristianMz21/JobsColombia/actions/workflows/lint.yml)

## Descripcion

Herramienta de scraping para extraer y analizar ofertas de empleo de tecnologia en Colombia desde multiples portales:

- LinkedIn
- Indeed
- elempleo.com
- computrabajo.com
- mitrabajo.co

## Caracteristicas

- Extraccion multi-portal de ofertas de empleo tech
- Sistema de scoring y clasificacion de relevancia
- Filtrado de empresas de outsourcing (BairesDev, Turing, Crossover, etc.)
- Deduplicacion de ofertas
- Soporte para proxies dinamicos
- Proteccion anti-deteccion (Cloudflare bypass, User-Agent rotation)
- Logging profesional
- Exportacion a CSV

## Requisitos

- Python 3.11+
- uv (gestor de paquetes)

## Instalacion

```bash
# Clonar el repositorio
git clone https://github.com/CristianMz21/JobsColombia.git
cd JobsColombia

# Instalar dependencias con uv
uv sync

# Opcional: Instalar dependencias de desarrollo
uv sync --dev
```

## Uso

```bash
# Ejecutar el scraper
python main.py
```

El script extraera ofertas de empleo y las guardara en un archivo CSV con marcas de tiempo.

## Configuracion

La configuracion se encuentra en `src/config.py`:

- **Terminos de busqueda**: Palabras clave para la busqueda de empleo
- **Ponderaciones de scoring**: Pesos para tecnologias, modalidad, experiencia
- **Configuracion anti-deteccion**: Delay entre requests, timeouts, reintentos
- **Blacklist de empresas**: Empresas de outsourcing a excluir

## Estructura del Proyecto

```
JobsColombia/
├── main.py                 # Punto de entrada
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuracion centralizada
│   ├── logger.py           # Configuracion de logging
│   ├── scoring.py          # Sistema de scoring
│   ├── scraping.py         # Funciones de scraping
│   ├── utils.py           # Utilidades
│   ├── utils_proxies.py    # Gestion de proxies
│   └── scrapers/          # Spiders para portales
│       ├── base.py
│       ├── computrabajo.py
│       └── elempleo.py
├── tests/                  # Pruebas unitarias
├── pyproject.toml         # Configuracion del proyecto
├── ruff.toml              # Configuracion de linting
└── .github/
    └── workflows/         # GitHub Actions
        ├── tests.yml
        └── lint.yml
```

## Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con coverage
pytest --cov=src --cov-report=term-missing
```

## Linting

```bash
# Verificar codigo
ruff check .

# Formatear codigo
ruff format .

# Auto-corregir problemas
ruff check --fix .
```

## Tech Stack

- **Python 3.11+** - Lenguaje principal
- **Scrapling** - Framework de web scraping
- **Pandas** - Manipulacion de datos
- **JobSpy** - Scraping de LinkedIn/Indeed
- **Requests** - HTTP client
- **Ruff** - Linting y formateo
- **Pytest** - Testing framework

## Disclaimer

Este proyecto es solo para fines educativos. Asegurate de cumplir con los Terminos de Servicio de los portales web antes de usar este scraper.

## Licencia

MIT License - consulta el archivo [LICENSE](LICENSE) para mas detalles.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerir cambios o mejoras.
