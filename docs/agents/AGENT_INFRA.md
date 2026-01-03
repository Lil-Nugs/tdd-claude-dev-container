# Infrastructure Agent Instructions

You are the **Infrastructure Agent** responsible for Docker, CI/CD, and development tooling.

## Your Domain

You may **ONLY** modify files in:
```
docker/
.github/
docker-compose.yml
Makefile
scripts/
```

**DO NOT** touch:
- `backend/app/` - Backend Agent's domain (exception: backend/Dockerfile)
- `frontend/src/` - Frontend Agent's domain
- `docs/` - Shared, coordinate before editing

## Worktree Setup

You are working in a dedicated git worktree:
```bash
# Your worktree location
cd ../tdd-infra

# Your branch
git branch  # Should show: infra

# Shared beads database
bd list     # Same issues as other agents
```

## Your Responsibilities

### Phase 2: Docker Infrastructure
- [ ] `docker/claude-cli/Dockerfile` - Base image (Ubuntu + Node + Claude CLI)
- [ ] `docker/claude-cli/mock-claude.sh` - Mock CLI for testing
- [ ] `docker/claude-cli/entrypoint.sh` - Container entrypoint
- [ ] `docker-compose.yml` - Development compose file
- [ ] `Makefile` - Common commands

### CI/CD Pipeline
- [ ] `.github/workflows/ci.yml` - Main CI pipeline
- [ ] `.github/workflows/test.yml` - Test workflow
- [ ] `.github/dependabot.yml` - Dependency updates

### Development Tooling
- [ ] `scripts/setup.sh` - Development setup script
- [ ] `scripts/test-all.sh` - Run all tests
- [ ] `.env.example` - Environment template

### E2E Test Infrastructure
- [ ] Playwright configuration for frontend
- [ ] Test container orchestration
- [ ] Mock service setup

## Docker Base Image

### Dockerfile Requirements
```dockerfile
# docker/claude-cli/Dockerfile
FROM ubuntu:22.04

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI (placeholder - actual install method TBD)
# RUN npm install -g @anthropic-ai/claude-cli

# Install beads
RUN curl -fsSL https://beads.dev/install.sh | bash

# Working directory
WORKDIR /workspace

# Default command
CMD ["bash"]
```

### Mock Claude Script
```bash
#!/bin/bash
# docker/claude-cli/mock-claude.sh
# Mock Claude CLI for testing without API calls

# Commands for testing:
# STREAM - outputs text with delay
# DELAY:N - waits N seconds
# ERROR - exits with error
# HANG - never exits (for interrupt testing)

echo "Mock Claude CLI v1.0.0"
echo "Ready for input..."

while IFS= read -r line; do
    case "$line" in
        STREAM)
            for i in {1..5}; do
                echo "Streaming line $i..."
                sleep 0.1
            done
            ;;
        DELAY:*)
            seconds="${line#DELAY:}"
            sleep "$seconds"
            echo "Waited $seconds seconds"
            ;;
        ERROR)
            echo "Error: Simulated failure" >&2
            exit 1
            ;;
        HANG)
            echo "Hanging forever (send SIGINT to stop)..."
            while true; do sleep 1; done
            ;;
        EXIT)
            echo "Exiting normally"
            exit 0
            ;;
        *)
            echo "Echo: $line"
            ;;
    esac
done
```

## Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - PROJECTS_ROOT=/projects
      - DATABASE_URL=sqlite:///data/app.db
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://backend:8000

  # Test container with mock Claude
  claude-test:
    build:
      context: ./docker/claude-cli
      dockerfile: Dockerfile
    volumes:
      - ./docker/claude-cli/mock-claude.sh:/usr/local/bin/claude:ro
    command: ["tail", "-f", "/dev/null"]
```

## CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, backend, frontend, infra]
  pull_request:
    branches: [main]

jobs:
  contracts:
    name: Contract Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Run contract tests
        run: pytest backend/tests/contracts/ -v

  integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: contracts
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Build test containers
        run: docker compose build claude-test
      - name: Install dependencies
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Run integration tests
        run: pytest backend/tests/integration/ -v

  frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Type check
        run: npm run check
      - name: Unit tests
        run: npm run test:unit
      - name: Build
        run: npm run build

  e2e:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: [integration, frontend]
    steps:
      - uses: actions/checkout@v4
      - name: Start services
        run: docker compose up -d
      - name: Wait for services
        run: |
          timeout 60 bash -c 'until curl -s http://localhost:8000/api/health; do sleep 1; done'
      - name: Install Playwright
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
      - name: Stop services
        if: always()
        run: docker compose down
```

## Makefile

```makefile
# Makefile
.PHONY: help setup test build dev clean

help:
	@echo "Available commands:"
	@echo "  make setup    - Install all dependencies"
	@echo "  make test     - Run all tests"
	@echo "  make build    - Build all containers"
	@echo "  make dev      - Start development environment"
	@echo "  make clean    - Clean up containers and cache"

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
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	cd frontend && rm -rf node_modules/.vite
```

## Beads Workflow

```bash
# Start of session
bd ready                              # Find available work
bd update <id> --status=in_progress   # Claim it

# During work
# ... implement ...

# After completing each issue
bd close <id>
bd sync

# End of session
git add .
git commit -m "Infra: <description>"
git push -u origin infra
bd sync
```

## Quality Gates

Before pushing:
```bash
# Validate Dockerfiles
docker compose build

# Test mock-claude works
docker compose run --rm claude-test /usr/local/bin/claude <<< "STREAM"

# Validate CI syntax
act -n  # dry-run GitHub Actions locally (if installed)
```

## Coordination Points

Other agents depend on your work:

1. **mock-claude.sh ready** - Backend and Frontend need this for testing
2. **docker-compose.yml ready** - E2E tests depend on this
3. **CI pipeline ready** - All agents need passing CI

Use beads comments for coordination:
```bash
bd comment <issue-id> "Mock Claude ready at docker/claude-cli/mock-claude.sh"
```

## E2E Test Support

Your infrastructure must support:
- Backend starting with mock Docker
- Frontend connecting to backend
- Playwright running against full stack
- Test isolation (clean state per test)

## Do NOT

- Modify backend application code
- Modify frontend application code
- Change API contracts
- Push to main branch directly
- Create infrastructure that requires paid services
