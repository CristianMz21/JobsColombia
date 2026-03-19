# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- This CHANGELOG file

### Dependencies
- Python 3.11+
- Scrapling framework for web scraping
- JobSpy for LinkedIn/Indeed
- Pandas for data manipulation
- Ruff for linting
- Pytest for testing
