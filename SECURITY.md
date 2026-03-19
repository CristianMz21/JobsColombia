# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please send an email to contact@jobscolombia.com. All security vulnerabilities will be promptly addressed.

Please include the following information:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

## Security Best Practices

When using this library:

1. **Input Validation**: Always validate and sanitize input data before passing to scoring functions
2. **Data Privacy**: Be careful when processing job data that may contain sensitive information
3. **CSV Export**: Generated CSV files may contain job listing URLs - handle appropriately

## Dependencies

This library aims to keep dependencies minimal. The current runtime dependency is:

- `pandas` - Data manipulation

Dev dependencies (not installed by default):
- `ruff` - Linting
- `pytest` - Testing
- `pytest-cov` - Code coverage
- `mypy` - Type checking
- `bandit` - Security linting
- `safety` - Vulnerability scanning
