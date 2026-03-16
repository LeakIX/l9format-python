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

.PHONY: all
all: format sort lint typecheck test security-check ## Run all quality checks

.PHONY: test
test: ## Run tests using pytest
	uv run pytest

.PHONY: format
format: ## Format code using black
	uv run black .

.PHONY: check-format
check-format: ## Check code formatting with black
	uv run black --check .

.PHONY: sort
sort: ## Sort imports using isort
	uv run isort .

.PHONY: check-sort
check-sort: ## Check import sorting with isort
	uv run isort --check-only .

.PHONY: lint
lint: ## Lint code using ruff
	uv run ruff check .

.PHONY: lint-fix
lint-fix: ## Lint and fix code using ruff
	uv run ruff check --fix .

.PHONY: lint-shell
lint-shell: ## Lint shell scripts using shellcheck
	shellcheck .github/scripts/*.sh

.PHONY: typecheck
typecheck: ## Run mypy type checker
	uv run mypy l9format

.PHONY: security-check
security-check: ## Check for vulnerable dependencies using pip-audit
	uv run pip-audit

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
			'echo "Processing: $$1"; $(SED) -i -e "s/[[:space:]]*$$//" "$$1"' \
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

.PHONY: install
install: ## Install dependencies with uv
	uv sync

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
publish: build ## Publish to PyPI, tag and create GitHub release
	uv publish
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	git push origin "v$(VERSION)"
	gh release create "v$(VERSION)" dist/* \
		--title "v$(VERSION)" \
		--notes "Release v$(VERSION)"

.PHONY: clean-dist
clean-dist: ## Clean distribution artifacts
	rm -rf dist/

.PHONY: clean
clean: clean-dist ## Clean build artifacts and caches
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
