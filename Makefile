# Makefile for l9format-python project

VERSION := $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    SED := $(shell command -v gsed 2>/dev/null)
    ifeq ($(SED),)
        $(error GNU sed (gsed) not found on macOS. \
			Install with: brew install gnu-sed)
    endif
else
    SED := sed
endif

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup: ## Setup development environment
	uv sync

.PHONY: install
install: ## Install dependencies with uv
	uv sync

.PHONY: format
format: ## Format code
	uv run ruff format l9format tests
	uv run ruff check --fix l9format tests

.PHONY: check-format
check-format: ## Check code formatting
	uv run ruff format --check l9format tests
	uv run ruff check l9format tests

.PHONY: lint
lint: ## Run linter
	uv run ruff check l9format tests

.PHONY: typecheck
typecheck: ## Run type checker
	uv run mypy l9format

.PHONY: test
test: ## Run tests
	uv run pytest

.PHONY: coverage
coverage: ## Run tests with coverage (fails under 90%)
	uv run pytest --cov=l9format --cov-report=term-missing \
		--cov-report=xml --cov-fail-under=90

.PHONY: test-all
test-all: ## Run tests across all supported Python versions (nox)
	uv run nox -s tests

.PHONY: audit
audit: ## Audit dependencies for known vulnerabilities
	uv run pip-audit --skip-editable --progress-spinner=off

.PHONY: zizmor
zizmor: ## Audit GitHub Actions workflows for security issues
	uv run zizmor --offline .github/workflows/

.PHONY: sbom
sbom: ## Generate a CycloneDX SBOM of runtime dependencies
	uv export --format requirements-txt --no-dev --no-emit-project \
		--no-hashes -o sbom-requirements.txt
	uv run cyclonedx-py requirements sbom-requirements.txt \
		-o sbom.cdx.json
	rm -f sbom-requirements.txt

.PHONY: docs
docs: ## Build the documentation site (strict)
	uv run mkdocs build --strict

.PHONY: docs-serve
docs-serve: ## Serve the documentation locally
	uv run mkdocs serve

.PHONY: lint-shell
lint-shell: ## Lint shell scripts using shellcheck
	shellcheck .github/scripts/*.sh

.PHONY: check
check: check-format lint typecheck coverage ## Run all checks

.PHONY: fix-trailing-whitespace
fix-trailing-whitespace: ## Remove trailing whitespaces from all files
	@echo "Removing trailing whitespaces from all files..."
	@find . -type f \( \
		-name "*.py" -o -name "*.toml" -o -name "*.md" -o -name "*.yaml" \
		-o -name "*.yml" -o -name "*.json" \) \
		-not -path "./.git/*" \
		-not -path "./.venv/*" \
		-not -path "./__pycache__/*" \
		-exec sh -c \
			'$(SED) -i -e "s/[[:space:]]*$$//" "$$1"' \
			_ {} \; && \
		echo "Trailing whitespaces removed."

.PHONY: check-trailing-whitespace
check-trailing-whitespace: ## Check for trailing whitespaces in source files
	@echo "Checking for trailing whitespaces..."
	@files_with_trailing_ws=$$(find . -type f \( \
		-name "*.py" -o -name "*.toml" -o -name "*.md" -o -name "*.yaml" \
		-o -name "*.yml" -o -name "*.json" \) \
		-not -path "./.git/*" \
		-not -path "./.venv/*" \
		-not -path "./__pycache__/*" \
		-exec grep -l '[[:space:]]$$' {} + 2>/dev/null || true); \
	if [ -n "$$files_with_trailing_ws" ]; then \
		echo "Files with trailing whitespaces found:"; \
		echo "$$files_with_trailing_ws" | sed 's/^/  /'; \
		echo ""; \
		echo "Run 'make fix-trailing-whitespace' to fix automatically."; \
		exit 1; \
	else \
		echo "No trailing whitespaces found."; \
	fi

.PHONY: build
build: clean-dist ## Build package for distribution
	uv build

.PHONY: publish-dry-run
publish-dry-run: build ## Dry-run: show what would be published
	@echo "Would publish l9format v$(VERSION)"
	@echo "Would create tag: v$(VERSION)"
	@echo "Would create GitHub release: v$(VERSION)"
	@echo "Package contents:"
	@ls -lh dist/
	uv publish --dry-run

.PHONY: publish
publish: build sbom ## Publish to PyPI, tag and create GitHub release
	uv publish
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	git push origin "v$(VERSION)"
	gh release create "v$(VERSION)" dist/* sbom.cdx.json \
		--title "v$(VERSION)" \
		--notes "Release v$(VERSION)"

.PHONY: clean-dist
clean-dist: ## Clean distribution artifacts
	rm -rf dist/

.PHONY: clean
clean: clean-dist ## Clean build artifacts and caches
	rm -rf .pytest_cache .mypy_cache .ruff_cache .nox site \
		.coverage coverage.xml sbom.cdx.json
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
