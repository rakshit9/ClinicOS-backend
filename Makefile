# Clinic Auth API Makefile

.PHONY: help install dev test lint format clean run build

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Run development server"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  clean      - Clean up temporary files"
	@echo "  run        - Run production server"
	@echo "  build      - Build Docker image"

# Install dependencies
install:
	pip install -r requirements.txt

# Run development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	python -m pytest tests/ -v

# Run linting
lint:
	ruff check app/
	mypy app/

# Format code
format:
	black app/
	isort app/

# Clean up temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Run production server
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Build Docker image
build:
	docker build -t clinic-auth-api .
