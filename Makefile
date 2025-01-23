# Makefile for pygins project

.PHONY: test format sort lint security-check all

# Run all quality checks
all: test format sort lint security-check

# Run tests using pytest
test:
	poetry run pytest

# Format code using black
format:
	poetry run black .

# Sort imports using isort
sort:
	poetry run isort .

# Lint code using ruff
lint:
	poetry run ruff check .

# Check for vulnerable dependencies using pip-audit
security-check:
	poetry run pip-audit

