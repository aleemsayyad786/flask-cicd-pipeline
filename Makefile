.PHONY: help install test lint build run stop clean

help:                   ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:                ## Install dependencies
	pip install -r requirements.txt

test:                   ## Run test suite with coverage
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80

lint:                   ## Run flake8 linter
	flake8 app/ tests/ --max-line-length=100

build:                  ## Build Docker image
	docker build -t flask-cicd-demo:local .

run:                    ## Start app with Docker Compose
	docker compose up -d
	@echo "App running at http://localhost:5000"

stop:                   ## Stop Docker Compose
	docker compose down

logs:                   ## Tail app logs
	docker compose logs -f app

clean:                  ## Remove containers, images, caches
	docker compose down --rmi local --volumes --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage coverage.xml htmlcov/
