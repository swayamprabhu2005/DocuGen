# Contributing to DocuGen AI

Thank you for your interest in contributing! We welcome issues, bug reports, feature requests, and pull requests.

---

## Development Setup

```bash
git clone https://github.com/your-org/docugen-ai.git
cd docugen-ai
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v --tb=short
```

## Code Style

We use `ruff` for linting and formatting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Type Checking

```bash
mypy src/docugen/
```

## Submitting a Pull Request

1. Fork the repo and create a branch: `git checkout -b feat/my-feature`
2. Make changes and add tests
3. Ensure `pytest` and `ruff check` both pass
4. Write a clear PR description explaining *what* and *why*

## Reporting Issues

Please include:
- Python version
- `docugen` version (`python -c "import docugen; print(docugen.__version__)"`)
- Minimal reproducible example

## Code of Conduct

Be respectful. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).
