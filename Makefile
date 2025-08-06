.PHONY: help install dev test test-cov test-watch clean

help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	poetry install

dev: ## Start development server
	poetry run python app.py

start: ## Start the application
	poetry run python app.py

test: ## Run tests
	poetry run python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	poetry run python -m pytest --cov=src/ragspace --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	poetry run python -m pytest --watch

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

update: ## Update dependencies
	poetry update

add: ## Add a dependency (usage: make add PACKAGE=package-name)
	poetry add $(PACKAGE)

add-dev: ## Add a development dependency (usage: make add-dev PACKAGE=package-name)
	poetry add --group dev $(PACKAGE)

shell: ## Activate poetry shell
	poetry shell

build: ## Build the package
	poetry build

publish: ## Publish to PyPI
	poetry publish 