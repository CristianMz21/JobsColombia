# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-03-19

### Changed
- Improved type annotations and mypy compliance
- Updated GitHub Actions to latest versions (upload/download-artifact v7, codecov-action v5, setup-uv v7)
- Removed empty env blocks from workflows

### Added
- Comprehensive GitHub Actions workflows:
  - Tests with coverage and type checking
  - Lint with ruff and commit message validation
  - Build and verify wheel/sdist
  - Publish to PyPI
  - Security audit (pip-audit, safety, bandit)
- Dependabot configuration for automated dependency updates
- SECURITY.md policy document
- Full multi-portal scraping: LinkedIn, Indeed, elempleo.com, computrabajo.com, mitrabajo.co

## [0.1.0] - 2026-03-19

### Added
- Multi-portal job scraping support (LinkedIn, Indeed, elempleo.com, computrabajo.com, mitrabajo.co)
- Scoring and classification system for job relevance
- Outsourcing company filtering (BairesDev, Turing, Crossover, etc.)
- Job deduplication
- Dynamic proxy support
- Anti-detection protection (Cloudflare bypass, User-Agent rotation)
- Professional logging with rotating file handler
- CSV export with UTF-8-BOM encoding
- Comprehensive unit tests
- GitHub Actions CI/CD (tests and linting)
- Docker support

### Dependencies
- Python 3.11+
- Scrapling framework for web scraping
- JobSpy for LinkedIn/Indeed
- Pandas for data manipulation
- Ruff for linting
- Pytest for testing
