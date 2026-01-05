# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-04

### Added

#### Backend (FastAPI)
- Project management REST API (CRUD operations)
- Docker container lifecycle management (create, start, stop, remove)
- WebSocket terminal with PTY support for interactive sessions
- SQLModel ORM with SQLite database
- Command allowlist security for terminal sessions
- Working directory validation for security
- Docker Manager service wrapping Docker SDK
- CLI Runner service for PTY process management
- Health check endpoint with Docker status
- Async support throughout with aiosqlite

#### Frontend (SvelteKit PWA)
- Dashboard with project overview and statistics
- Projects list with create/delete functionality
- Project detail page with container controls
- Browser-based terminal using xterm.js
- WebSocket manager with automatic reconnection
- TypeScript type definitions matching backend contracts
- Type guards for runtime validation
- Responsive design with CSS variables

#### Infrastructure
- Docker Compose for development orchestration
- Backend Dockerfile with multi-stage build
- Frontend Dockerfile for SvelteKit
- Test container with mock Claude CLI
- Environment variable configuration

#### Testing
- Contract tests ensuring frontend/backend type alignment
- Unit tests for all routers and services
- Integration tests for CLI runner and Docker manager
- WebSocket protocol tests for terminal functionality
- pytest configuration with async support

#### Documentation
- Comprehensive README with quick start guide
- API documentation with all endpoints
- Architecture documentation with diagrams
- Contract documentation with type mappings
- User guide for end users

### Technical Details

#### API Endpoints
- `GET /health` - Health check with Docker status
- `GET/POST/PATCH/DELETE /api/projects` - Project CRUD
- `GET/POST/DELETE /api/containers` - Container management
- `POST /api/containers/{id}/start` - Start container
- `POST /api/containers/{id}/stop` - Stop container
- `GET /api/images` - List Docker images
- `WS /api/terminal/{session_id}` - Terminal WebSocket

#### WebSocket Protocol
- JSON-based message format
- Commands: spawn, input, interrupt, resize, ping
- Responses: output, status, pong

#### Security Measures
- Command allowlist: bash, sh, python, node, git, etc.
- Path restrictions: /home, /tmp, /projects, /workspace
- No authentication (configure CORS for production)

### Known Issues

- CORS configured for all origins (development only)
- No authentication/authorization system
- Terminal sessions are memory-resident (not persistent)
- SQLite not suitable for high-concurrency deployments
- Missing Makefile for common operations
- Missing CI/CD GitHub Actions workflows
- PWA service worker and icons not implemented

### Dependencies

#### Backend
- FastAPI 0.109+
- SQLModel 0.0.14+
- Pydantic 2.5+
- Docker SDK 7.0+
- uvicorn 0.27+
- aiosqlite 0.19+

#### Frontend
- SvelteKit (latest)
- TypeScript 5.x
- xterm.js (latest)
- Vite (latest)

---

## [Unreleased]

### Planned
- User authentication (OAuth/JWT)
- Project templates and scaffolding
- Multi-container workflow support
- Session persistence and replay
- Collaborative terminal sharing
- CI/CD pipeline with GitHub Actions
- PWA service worker and offline support
