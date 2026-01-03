# Makefile
# Common commands for TDD Claude project

.PHONY: help setup test build dev clean test-contracts test-integration test-frontend test-e2e

help:
	@echo "Available commands:"
	@echo "  make setup    - Install all dependencies"
	@echo "  make test     - Run all tests"
	@echo "  make build    - Build all containers"
	@echo "  make dev      - Start development environment"
	@echo "  make clean    - Clean up containers and cache"
	@echo ""
	@echo "Individual test targets:"
	@echo "  make test-contracts    - Run contract tests"
	@echo "  make test-integration  - Run integration tests"
	@echo "  make test-frontend     - Run frontend unit tests"
	@echo "  make test-e2e          - Run E2E tests"

setup:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install
	docker compose build

test: test-contracts test-integration test-frontend

test-contracts:
	pytest backend/tests/contracts/ -v

test-integration:
	pytest backend/tests/integration/ -v

test-frontend:
	cd frontend && npm run test:unit

test-e2e:
	cd frontend && npm run test:e2e

build:
	docker compose build

dev:
	docker compose up

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf node_modules/.vite 2>/dev/null || true
