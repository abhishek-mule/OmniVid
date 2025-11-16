.PHONY: test test-unit test-integration test-e2e coverage lint format check-style check-types install-dev clean help

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
COVERAGE = coverage
BLACK = black
ISORT = isort
MYPY = mypy
FLAKE8 = flake8

# Default target
help:
	@echo "Available targets:"
	@echo "  install-dev    Install development dependencies"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests"
	@echo "  test-integration  Run integration tests"
	@echo "  test-e2e       Run end-to-end tests"
	@echo "  coverage       Generate test coverage report"
	@echo "  lint           Run all linters"
	@echo "  format         Format code with Black and isort"
	@echo "  check-style    Check code style"
	@echo "  check-types    Run type checking"
	@echo "  clean          Clean up temporary files"

# Install development dependencies
install-dev:
	$(PIP) install -r requirements.txt -r requirements-test.txt
	$(PIP) install black isort mypy flake8

# Run all tests
test:
	$(PYTEST) tests/

# Run unit tests
test-unit:
	$(PYTEST) tests/unit/

# Run integration tests
test-integration:
	$(PYTEST) tests/integration/

# Run end-to-end tests
test-e2e:
	$(PYTEST) tests/e2e/

# Generate coverage report
coverage:
	$(PYTEST) --cov=src --cov-report=term-missing --cov-report=html tests/

# Run all linters
lint: check-style check-types

# Format code
format:
	$(BLACK) src tests
	$(ISORT) src tests

# Check code style
check-style:
	$(BLACK) --check src tests
	$(ISORT) --check-only src tests
	$(FLAKE8) src tests

# Run type checking
check-types:
	$(MYPY) src

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	rm -rf .coverage htmlcov/ .mypy_cache/ .pytest_cache/
