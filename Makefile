.PHONY: help install dev start stop clean test lint format check

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Start development server"
	@echo "  start       - Start production server"
	@echo "  stop        - Stop all services"
	@echo "  clean       - Clean up containers and volumes"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  check       - Run all checks (lint + format)"

# Install dependencies
install:
	pip install -r requirements.txt

# Development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
start:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start database services
db-up:
	docker-compose up -d mongodb mongo-express

# Stop all services
stop:
	docker-compose down

# Clean up everything
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Run tests
test:
	python -m pytest tests/ -v

# Lint code
lint:
	ruff check app/ tests/
	mypy app/

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Run all checks
check: lint format

# Setup development environment
setup: install db-up
	@echo "✅ Development environment ready!"
	@echo "📝 Copy env.example to .env and update configuration"
	@echo "🚀 Run 'make dev' to start the development server"
