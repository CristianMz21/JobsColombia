# Contributing to TechJobs Colombia

Thank you for your interest in contributing!

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce
   - Expected vs actual behavior

### Suggesting Features

1. Open a new issue with the label "enhancement"
2. Describe the feature in detail
3. Explain why it would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes following our code style
4. Run tests: `pytest`
5. Run linting: `ruff check . && ruff format .`
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/CristianMz21/JobsColombia.git
cd JobsColombia

# Install dependencies
uv sync --all-extras

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

## Code Style

- Follow PEP 8
- Use type hints
- Use Ruff for formatting and linting
- Write tests for new features

## Testing

- All tests must pass before merging
- Aim for >80% code coverage
- Test both positive and negative cases

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
