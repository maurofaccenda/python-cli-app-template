.PHONY: help install install-dev test test-cov lint format clean build check-all

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with Ruff"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  security     - Run security checks with bandit"
	@echo "  check-all    - Run all quality checks"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build the package"
	@echo "  install-app  - Install the CLI app in development mode"

# Install production dependencies
install:
	uv sync

# Install development dependencies
install-dev:
	uv sync --group dev

# Install the CLI app in development mode
install-app:
	uv pip install -e .

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=cli_app --cov-report=html --cov-report=term-missing

# Run linting checks
lint:
	uv run ruff check cli_app/ tests/

# Format code
format:
	uv run ruff format cli_app/ tests/

# Run type checking
type-check:
	uv run mypy cli_app/

# Run security checks
security:
	uv run bandit -r cli_app/ -f json -o bandit-report.json

# Run all quality checks
check-all: lint type-check security test

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Build the package
build:
	uv run python -m build

# Install pre-commit hooks
install-hooks:
	uv run pre-commit install

# Run pre-commit on all files
pre-commit-all:
	uv run pre-commit run --all-files

# Show project info
info:
	@echo "Python CLI Application Template"
	@echo "=============================="
	@echo "Package: cli_app"
	@echo "CLI Command: cli-app"
	@echo ""
	@echo "Available commands:"
	@echo "  cli-app --help"
	@echo "  cli-app configure --endpoint <url> --token <token>"
	@echo "  cli-app status"
	@echo "  cli-app fetch --resource <resource>"
	@echo "  cli-app create --resource <resource> --data <json>" 