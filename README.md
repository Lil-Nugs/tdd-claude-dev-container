# TDD Claude Dev Container

A web-based development environment manager for AI-powered coding with Claude CLI. Create isolated Docker containers, manage projects, and interact with Claude through a browser-based terminal.

## Features

- **Project Management** - Create, list, and manage development projects
- **Docker Container Lifecycle** - Start, stop, and monitor isolated Claude CLI environments
- **Browser-based Terminal** - Full PTY terminal with xterm.js, supporting all terminal interactions
- **WebSocket Streaming** - Real-time bidirectional communication for terminal I/O
- **PWA Frontend** - Responsive SvelteKit application with offline capabilities
- **Type-safe Contracts** - Shared Pydantic/TypeScript types ensuring frontend-backend alignment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+
- Python 3.11+
- uv (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/tdd-claude-dev-container.git
cd tdd-claude-dev-container

# Start all services
docker compose up -d

# Or run services separately:

# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### Running

Open http://localhost:5173 in your browser.

## Development

### Project Structure

```
tdd-claude-dev-container/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/          # Pydantic models and contracts
│   │   ├── routers/         # API route handlers
│   │   ├── services/        # Docker manager, CLI runner
│   │   └── websockets/      # Terminal WebSocket handler
│   └── tests/               # pytest test suite
├── frontend/                # SvelteKit PWA
│   └── src/
│       ├── lib/
│       │   ├── api/         # API client and WebSocket manager
│       │   ├── components/  # Svelte components
│       │   └── types/       # TypeScript type definitions
│       └── routes/          # SvelteKit pages
├── docker/                  # Docker configurations
│   └── claude-cli/          # Test container with mock Claude
└── docs/                    # Documentation
    ├── api/                 # API documentation
    ├── architecture/        # System architecture
    ├── contracts/           # Type contract documentation
    └── user-guide/          # End-user guide
```

### Running Tests

```bash
# All backend tests
cd backend
uv run pytest tests/ -v

# Contract tests only
uv run pytest tests/contracts/ -v

# Frontend checks
cd frontend
npm run check
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
DOCKER_SOCKET=unix:///var/run/docker.sock
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## API Documentation

See [docs/api/](docs/api/) for complete API documentation including:
- REST endpoints for projects and containers
- WebSocket protocol for terminal streaming
- Request/response formats

## Architecture

See [docs/architecture/](docs/architecture/) for system architecture including:
- Component diagrams
- Data flow descriptions
- Technology stack details

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/ -v`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Workflow

This project uses a TDD (Test-Driven Development) approach:

1. **Contract Tests First** - Define types in `backend/app/models/contracts.py`
2. **Frontend Types** - Mirror in `frontend/src/lib/types/api.ts`
3. **Integration Tests** - Write tests before implementation
4. **Implementation** - Build to pass tests

## License

MIT
