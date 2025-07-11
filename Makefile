# Document Processing Pipeline Makefile
# Handles: Markdown → PDF → SVG → PNG → OCR → Search → Aggregation
# Enhanced with universal converter capabilities and development tools

SHELL := /bin/bash
PYTHON := python3
PIP := pip3
VENV := venv
ACTIVATE := $(VENV)/bin/activate
OUTPUT_DIR := output
CONVERTER_DIR := ./converters
CONFIG_DIR := ./config

# Color definitions for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

# Logging functions
define log_info
	@echo -e "$(GREEN)[INFO]$(NC) $(1)"
endef

define log_warn
	@echo -e "$(YELLOW)[WARN]$(NC) $(1)"
endef

define log_error
	@echo -e "$(RED)[ERROR]$(NC) $(1)"
endef

define log_success
	@echo -e "$(PURPLE)[SUCCESS]$(NC) $(1)"
endef

# Default target
.PHONY: all
all: install create process aggregate search
	$(call log_success,Document processing pipeline completed successfully!)

# Run commands using Poetry
.PHONY: run-commands
run-commands:
	$(call log_info,Running text2api commands with Poetry...)
	poetry run text2api generate "API do zarządzania użytkownikami z CRUD operations"
	poetry run text2api generate "System czatu" --type websocket --framework websockets
	poetry run text2api generate "Blog API" --no-docker --no-tests
	poetry run text2api generate-from-file --interactive
	poetry run text2api check
	$(call log_success,Commands executed successfully!)

# Push changes to remote repository
.PHONY: push
push:
	$(call log_info,Staging all changes...)
	if [ -d .git ]; then \
		git add . && \
		git diff --cached --quiet && \
		{ echo "No changes to commit"; exit 0; } || \
		{ \
			echo "Committing changes..." && \
			git commit -m "Update: $(shell date +'%Y-%m-%d %H:%M:%S')" && \
			echo "Pushing to remote..." && \
			git push origin $(shell git rev-parse --abbrev-ref HEAD) 2>/dev/null; \
			if [ $$? -ne 0 ]; then \
				echo "Failed to push to remote. This might be due to authentication issues."; \
				echo "Please ensure you have the correct permissions to push to the repository."; \
				echo "You may need to set up SSH keys or use a personal access token."; \
				exit 1; \
			fi; \
		} \
	else \
		$(call log_error,Not a git repository); \
		exit 1; \
	fi
	$(call log_success,Changes pushed successfully!)

# Publish package to PyPI using Poetry
.PHONY: publish
publish: clean
	$(call log_info,Preparing to publish package...)
	@if [ -f "pyproject.toml" ]; then \
		echo "Building package..."; \
		poetry version patch && poetry build || { echo "Build failed"; exit 1; }; \
		echo "Publishing to PyPI..."; \
		poetry publish || { echo "Publish failed"; exit 1; }; \
	else \
		echo "pyproject.toml not found. Not a Poetry project?"; \
		exit 1; \
	fi
	$(call log_success,Package published successfully!)

# Install all required dependencies
.PHONY: install
install: install-system-deps
	$(call log_info,Installing dependencies with Poetry...)
	poetry install --with dev
	$(call log_success,Dependencies installed successfully!)

# Install development dependencies (alias for install)
.PHONY: install-dev
install-dev: install

# Install system dependencies
.PHONY: install-system-deps
install-system-deps:
	$(call log_info,Checking system dependencies...)
	@if [ -f "$(CONFIG_DIR)/install_dependencies.sh" ]; then \
		bash $(CONFIG_DIR)/install_dependencies.sh; \
	else \
		echo -e "$(YELLOW)[WARN]$(NC) System dependency installer not found"; \
	fi

# Create example files
.PHONY: create
create:
	$(call log_info,Creating example markdown file...)
	. $(ACTIVATE) && $(PYTHON) processor.py --step create
	$(call log_success,Example files created!)

# Process documents through the pipeline
.PHONY: process
process:
	$(call log_info,Processing documents through pipeline...)
	. $(ACTIVATE) && $(PYTHON) processor.py --step process
	$(call log_success,Processing completed!)

# Aggregate results
.PHONY: aggregate
aggregate:
	$(call log_info,Aggregating results...)
	. $(ACTIVATE) && $(PYTHON) processor.py --step aggregate
	$(call log_success,Aggregation completed!)

# Search metadata
.PHONY: search
search:
	$(call log_info,Searching metadata...)
	. $(ACTIVATE) && $(PYTHON) processor.py --step search
	$(call log_success,Search completed!)

# Universal file conversion function
define convert_file
	@if [ ! -f "$(CONVERTER_DIR)/$(1).sh" ]; then \
		$(call log_error,Converter $(1) not found); \
		exit 1; \
	fi; \
	if [ -z "$(2)" ] || [ -z "$(3)" ] || [ -z "$(4)" ]; then \
		$(call log_error,Missing arguments); \
		echo "Usage: make convert CONVERTER=$(1) FROM=$(2) TO=$(3) INPUT=$(4) [OUTPUT=$(5)]"; \
		exit 1; \
	fi; \
	OUTPUT_FILE="$(if $(5),$(5),$(basename $(4)).$(3))"; \
	$(call log_info,Converting with $(1): $(4) ($(2)) -> $OUTPUT_FILE ($(3))); \
	bash $(CONVERTER_DIR)/$(1).sh "$(2)" "$(3)" "$(4)" "$OUTPUT_FILE"
endef

# Convert files using external converters
.PHONY: convert
convert:
	$(call convert_file,$(CONVERTER),$(FROM),$(TO),$(INPUT),$(OUTPUT))

# Image conversion shortcuts
.PHONY: img-convert
img-convert:
	$(call convert_file,imagemagick,$(FROM),$(TO),$(INPUT),$(OUTPUT))

.PHONY: pdf-convert
pdf-convert:
	$(call convert_file,pandoc,$(FROM),$(TO),$(INPUT),$(OUTPUT))

# Development Commands
.PHONY: help install test test-unit test-integration test-functional test-performance test-slow test-ollama test-docker test-coverage lint format format-check clean

help:  ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

# Installation
install:  ## Install dependencies
	poetry install --with dev

# Testing
.PHONY: test
test:  ## Run all tests
	poetry run pytest

.PHONY: test-unit
test-unit:  ## Run unit tests only
	poetry run pytest tests/unit -v

.PHONY: test-integration
test-integration:  ## Run integration tests only
	poetry run pytest tests/integration -v

.PHONY: test-functional
test-functional:  ## Run functional tests only
	poetry run pytest tests/functional -v

.PHONY: test-performance
test-performance:  ## Run performance tests only
	poetry run pytest -m performance -v

.PHONY: test-slow
test-slow:  ## Run slow tests
	poetry run pytest -m slow -v

.PHONY: test-ollama
test-ollama:  ## Run tests requiring Ollama
	poetry run pytest -m requires_ollama -v

.PHONY: test-docker
test-docker:  ## Run tests requiring Docker
	poetry run pytest -m requires_docker -v

.PHONY: test-coverage
test-coverage:  ## Run tests with coverage
	poetry run pytest --cov=text2api --cov-report=html --cov-report=term

# Code Quality
.PHONY: lint
lint:  ## Run linting
	poetry run flake8 text2api tests
	poetry run mypy text2api

.PHONY: format
format:  ## Format code
	poetry run black text2api tests
	poetry run isort text2api tests

.PHONY: format-check
format-check:  ## Check code formatting
	poetry run black --check text2api tests
	poetry run isort --check-only text2api tests

# Cleanup
.PHONY: clean
clean:  ## Clean up temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf html

# Documentation
.PHONY: docs
docs:  ## Generate documentation
	poetry run mkdocs build

# Docker
.PHONY: docker
docker:  ## Build and run with Docker
	docker-compose up --build

# Preserve existing test command
.PHONY: test-original
test-original: install
	$(call log_info,Running tests...)
	. $(ACTIVATE) && python test_environment.py
	@if [ -f "tests/test_processor.py" ]; then \
		. $(ACTIVATE) && pytest tests/ -v --cov=processor; \
	else \
		$(call log_warn,No tests found, running environment verification only); \
	fi
	$(call log_success,Tests completed!)

# Benchmark the pipeline
.PHONY: benchmark
benchmark:
	$(call log_info,Running pipeline benchmark...)
	. $(ACTIVATE) && time $(PYTHON) processor.py --step process
	$(call log_success,Benchmark completed!)

# Validate output files
.PHONY: validate
validate:
	$(call log_info,Validating output files...)
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		for file in $(OUTPUT_DIR)/*.pdf; do \
			if [ -f "$file" ]; then \
				echo "✓ PDF: $file"; \
			fi; \
		done; \
		for file in $(OUTPUT_DIR)/*.svg; do \
			if [ -f "$file" ]; then \
				echo "✓ SVG: $file"; \
			fi; \
		done; \
		for file in $(OUTPUT_DIR)/*.png; do \
			if [ -f "$file" ]; then \
				echo "✓ PNG: $file"; \
			fi; \
		done; \
		for file in $(OUTPUT_DIR)/*.json; do \
			if [ -f "$file" ]; then \
				. $(ACTIVATE) && python -m json.tool "$file" > /dev/null && echo "✓ JSON: $file"; \
			fi; \
		done; \
	else \
		$(call log_warn,Output directory not found); \
	fi
	$(call log_success,Validation completed!)

# List supported formats
.PHONY: list-formats
list-formats:
	$(call log_info,Supported input/output formats:)
	@echo -e "$(CYAN)Input formats:$(NC)"
	@echo "  - Markdown (.md)"
	@echo "  - Text (.txt)"
	@echo "  - HTML (.html)"
	@echo ""
	@echo -e "$(CYAN)Output formats:$(NC)"
	@echo "  - PDF (.pdf)"
	@echo "  - SVG (.svg)"
	@echo "  - PNG (.png)"
	@echo "  - JSON metadata (.json)"
	@echo "  - HTML dashboard (.html)"

# Check system requirements
.PHONY: check-system
check-system:
	$(call log_info,Checking system requirements...)
	@echo "Python: $($(PYTHON) --version 2>/dev/null || echo 'Not found')"
	@echo "Tesseract: $(tesseract --version 2>/dev/null | head -n1 || echo 'Not found')"
	@echo "Poppler: $(pdftoppm -v 2>&1 | head -n1 || echo 'Not found')"
	@echo "Cairo: $(pkg-config --modversion cairo 2>/dev/null || echo 'Not found')"
	@echo "ImageMagick: $(convert -version 2>/dev/null | head -n1 || echo 'Not found')"

# Create project structure
.PHONY: init-project
init-project:
	$(call log_info,Initializing project structure...)
	@mkdir -p $(OUTPUT_DIR) $(CONVERTER_DIR) $(CONFIG_DIR) tests docs examples
	@touch $(CONVERTER_DIR)/.gitkeep $(CONFIG_DIR)/.gitkeep tests/.gitkeep
	$(call log_success,Project structure initialized!)

# Package and distribute
.PHONY: package
package: clean test lint
	$(call log_info,Creating distribution package...)
	@mkdir -p dist
	@tar -czf dist/document-processor-$(date +%Y%m%d).tar.gz \
		--exclude=venv --exclude=dist --exclude=__pycache__ \
		--exclude=.git --exclude=*.pyc .
	$(call log_success,Package created in dist/)

# Deploy to server (requires SSH config)
.PHONY: deploy
deploy: package
	$(call log_info,Deploying package...)
	@if [ -n "$(SERVER)" ]; then \
		scp dist/*.tar.gz $(SERVER):/tmp/; \
		$(call log_success,Package deployed to $(SERVER)); \
	else \
		$(call log_error,SERVER variable not set); \
		echo "Usage: make deploy SERVER=user@hostname"; \
	fi

# Monitor processing (runs pipeline and watches files)
.PHONY: monitor
monitor:
	$(call log_info,Starting monitoring mode...)
	@echo "Watching for changes in current directory..."
	@while true; do \
		inotifywait -e modify,create,delete . 2>/dev/null && \
		echo "Change detected, running pipeline..." && \
		$(MAKE) process; \
	done

# Generate documentation
.PHONY: docs
docs:  ## Generate documentation
	$(call log_info,Generating documentation...)
	@mkdir -p docs
	poetry run mkdocs build
	$(call log_success,Documentation generated in site/)

# Clean generated files
.PHONY: clean
clean:  ## Clean up temporary files
	$(call log_info,Cleaning generated files...)
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf html
	rm -f *.pdf *.svg *.png *.json *.html
	rm -rf $(OUTPUT_DIR)/ __pycache__/ *.pyc .pytest_cache/ .coverage
	$(call log_success,Cleanup completed!)

# Clean everything including virtual environment
.PHONY: clean-all
clean-all: clean
	$(call log_info,Removing virtual environment and distribution files...)
	@rm -rf $(VENV)/ dist/ .mypy_cache/
	$(call log_success,Full cleanup completed!)

# Show system status
.PHONY: status
status:
	@echo -e "$(BLUE)Document Processing Pipeline Status$(NC)"
	@echo "=================================="
	@echo ""
	@echo -e "$(CYAN)Environment:$(NC)"
	@echo "  Virtual env: $([ -d $(VENV) ] && echo '✓ Active' || echo '✗ Not found')"
	@echo "  Python: $($(PYTHON) --version 2>/dev/null || echo 'Not found')"
	@echo ""
	@echo -e "$(CYAN)Output Directory:$(NC)"
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		echo "  Files: $(ls -1 $(OUTPUT_DIR) 2>/dev/null | wc -l) items"; \
		echo "  Size: $(du -sh $(OUTPUT_DIR) 2>/dev/null | cut -f1)"; \
	else \
		echo "  Status: Not created"; \
	fi
	@echo ""
	@echo -e "$(CYAN)Last Run:$(NC)"
	@if [ -f "$(OUTPUT_DIR)/metadata.json" ]; then \
		echo "  Last processed: $(stat -c %y $(OUTPUT_DIR)/metadata.json 2>/dev/null | cut -d. -f1)"; \
	else \
		echo "  Status: Never run"; \
	fi

# Interactive mode
.PHONY: interactive
interactive:
	@echo -e "$(BLUE)Document Processing Pipeline - Interactive Mode$(NC)"
	@echo "================================================"
	@echo ""
	@echo "Select an option:"
	@echo "1. Create example and run full pipeline"
	@echo "2. Process existing files"
	@echo "3. Create dashboard only"
	@echo "4. Run tests"
	@echo "5. Check system status"
	@echo "6. Exit"
	@echo ""
	@read -p "Enter choice (1-6): " choice; \
	case $choice in \
		1) $(MAKE) all ;; \
		2) $(MAKE) process aggregate ;; \
		3) $(MAKE) aggregate ;; \
		4) $(MAKE) test ;; \
		5) $(MAKE) status ;; \
		6) echo "Goodbye!" ;; \
		*) echo "Invalid choice" ;; \
	esac

# Help target with enhanced information
.PHONY: help
help:  ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
	@echo "================================="
	@echo ""
	@echo -e "$(CYAN)Core Pipeline:$(NC)"
	@echo "  all           - Run complete pipeline (install → create → process → aggregate)"
	@echo "  install       - Install all dependencies"
	@echo "  create        - Create example markdown file"
	@echo "  process       - Process documents through pipeline"
	@echo "  aggregate     - Aggregate results into HTML table"
	@echo "  search        - Search metadata in filesystem"
	@echo ""
	@echo -e "$(CYAN)Development:$(NC)"
	@echo "  install-dev   - Install development dependencies"
	@echo "  format        - Format code with black and isort"
	@echo "  lint          - Lint code with flake8 and mypy"
	@echo "  test          - Run tests and validation"
	@echo "  benchmark     - Benchmark pipeline performance"
	@echo ""
	@echo -e "$(CYAN)File Conversion:$(NC)"
	@echo "  convert       - Universal file converter"
	@echo "  img-convert   - Image format conversion"
	@echo "  pdf-convert   - PDF conversion"
	@echo "  list-formats  - Show supported formats"
	@echo ""
	@echo -e "$(CYAN)Utilities:$(NC)"
	@echo "  validate      - Validate output files"
	@echo "  check-system  - Check system requirements"
	@echo "  status        - Show pipeline status"
	@echo "  monitor       - Watch for file changes"
	@echo "  interactive   - Interactive mode"
	@echo ""
	@echo -e "$(CYAN)Maintenance:$(NC)"
	@echo "  clean         - Remove generated files"
	@echo "  clean-all     - Remove everything including venv"
	@echo "  package       - Create distribution package"
	@echo "  docs          - Generate documentation"
	@echo ""
	@echo -e "$(CYAN)Examples:$(NC)"
	@echo "  make all                           # Complete pipeline"
	@echo "  make convert CONVERTER=imagemagick FROM=jpg TO=png INPUT=image.jpg"
	@echo "  make deploy SERVER=user@server     # Deploy to server"
	@echo "  make monitor                       # Watch for changes"

# Prevent make from interpreting arguments as targets
%:
	@: