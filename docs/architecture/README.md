# System Architecture

Technical architecture documentation for TDD Claude Dev Container.

## Overview

The system provides a web-based interface for managing AI-powered development containers. Users create projects, spawn Docker containers with Claude CLI, and interact through browser-based terminals.

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (PWA)                          │
│                  SvelteKit + xterm.js                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Dashboard  │  │  Projects   │  │  Terminal Component │  │
│  │    Page     │  │    Pages    │  │     (xterm.js)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
              REST API     │    WebSocket
              (HTTP)       │    (ws://)
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                      Backend (API)                           │
│                       FastAPI                                │
│  ┌─────────────────┬──────────────────┬──────────────────┐  │
│  │  Projects       │  Containers      │  Terminal        │  │
│  │  Router         │  Router          │  WebSocket       │  │
│  │  (CRUD)         │  (Docker ops)    │  Handler         │  │
│  └────────┬────────┴────────┬─────────┴────────┬─────────┘  │
│           │                 │                  │             │
│  ┌────────┴────────┐ ┌──────┴───────┐ ┌───────┴────────┐   │
│  │   SQLModel      │ │  Docker      │ │  CLI Runner    │   │
│  │   Database      │ │  Manager     │ │  (PTY)         │   │
│  └────────┬────────┘ └──────┬───────┘ └───────┬────────┘   │
└───────────┼─────────────────┼─────────────────┼─────────────┘
            │                 │                 │
     ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
     │   SQLite    │   │   Docker    │   │  PTY/fork   │
     │  Database   │   │   Socket    │   │  Processes  │
     └─────────────┘   └──────┬──────┘   └─────────────┘
                              │
              ┌───────────────┴───────────────┐
              │       Docker Containers        │
              │    (Claude CLI environments)   │
              └────────────────────────────────┘
```

## Component Descriptions

### Frontend (SvelteKit PWA)

**Technology:** SvelteKit, TypeScript, xterm.js

| Component | Location | Purpose |
|-----------|----------|---------|
| Dashboard | `routes/+page.svelte` | Project overview, stats, recent projects |
| Projects List | `routes/projects/+page.svelte` | Create and browse projects |
| Project Detail | `routes/projects/[id]/+page.svelte` | View project, manage container |
| Terminal | `routes/projects/[id]/terminal/+page.svelte` | Interactive terminal session |
| API Client | `lib/api/client.ts` | REST API wrapper with error handling |
| WebSocket Manager | `lib/api/websocket.ts` | WebSocket connection with reconnect |
| Terminal Component | `lib/components/Terminal.svelte` | xterm.js integration |

### Backend (FastAPI)

**Technology:** FastAPI, SQLModel, Docker SDK, asyncio

| Component | Location | Purpose |
|-----------|----------|---------|
| Projects Router | `app/routers/projects.py` | CRUD for project records |
| Containers Router | `app/routers/containers.py` | Docker container management |
| Terminal Handler | `app/websockets/terminal.py` | WebSocket terminal protocol |
| CLI Runner | `app/services/cli_runner.py` | PTY process management |
| Docker Manager | `app/services/docker_manager.py` | Docker SDK wrapper |
| Contracts | `app/models/contracts.py` | Shared type definitions |
| Database Models | `app/models/project.py` | SQLModel ORM models |

### Data Stores

| Store | Technology | Purpose |
|-------|------------|---------|
| Application DB | SQLite (aiosqlite) | Project metadata |
| Container Runtime | Docker | Isolated environments |
| Session State | In-memory | Active terminal sessions |

## Data Flow

### Project Creation

```
1. User submits "New Project" form
2. Frontend POST /api/projects with name
3. Backend validates, creates DB record
4. Response returns project with generated ID
5. Frontend navigates to project detail page
```

### Container Lifecycle

```
1. User clicks "Start Container"
2. Frontend POST /api/containers with config
3. DockerManager creates container via Docker SDK
4. Container ID stored, status returned
5. User can now open terminal
```

### Terminal Session

```
1. User clicks "Open Terminal"
2. Frontend opens WebSocket to /api/terminal/{session_id}
3. Frontend sends "spawn" command (e.g., ["bash"])
4. Backend creates PTY process via pty.fork()
5. Backend streams process output via WebSocket
6. User types in xterm.js
7. Frontend sends "input" messages
8. Backend writes to PTY fd
9. Process output read, sent as "output" messages
10. On disconnect/exit, process terminated
```

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| SvelteKit | Latest | Application framework |
| TypeScript | 5.x | Type safety |
| xterm.js | Latest | Terminal emulation |
| Vite | Latest | Build tooling |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.109+ | Web framework |
| SQLModel | 0.0.14+ | ORM with Pydantic |
| Pydantic | 2.5+ | Data validation |
| Docker SDK | 7.0+ | Container management |
| aiosqlite | 0.19+ | Async SQLite |
| uvicorn | 0.27+ | ASGI server |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| Docker | Container runtime |
| Docker Compose | Development orchestration |
| SQLite | Application database |

## Security Model

### Command Allowlist

The CLI Runner restricts executable commands:

```python
ALLOWED_COMMANDS = frozenset([
    "bash", "sh",
    "python", "python3",
    "node", "npm", "npx",
    "bd", "claude",
    "git", "make",
    "pytest", "ruff", "mypy",
    "pip", "uv"
])
```

### Path Restrictions

Working directories must be under allowed paths:

```python
ALLOWED_BASE_PATHS = [
    "/home",
    "/tmp",
    "/projects",
    "/workspace"
]
```

### Future Considerations

- Add authentication (OAuth, JWT)
- Configure CORS for specific domains
- Rate limiting
- Audit logging

## PTY Process Management

The terminal uses pseudo-terminal (PTY) for full terminal emulation:

```python
# Fork with PTY
pid, fd = pty.fork()
if pid == 0:
    # Child process: execute command
    os.execvpe(command[0], command, env)
else:
    # Parent: manage file descriptor
    # Set non-blocking I/O
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
```

**Benefits of PTY:**
- Full terminal emulation (colors, cursor movement)
- Signal handling (Ctrl+C sends SIGINT)
- Terminal resize support (TIOCSWINSZ)
- Interactive program support (vim, less, etc.)

## WebSocket Protocol

JSON-based bidirectional communication:

```
Client                          Server
  │                               │
  │──── spawn {command} ─────────>│
  │                               │ (creates PTY process)
  │<──── status {running} ────────│
  │                               │
  │<──── output {data} ───────────│
  │                               │
  │──── input {data} ────────────>│
  │                               │ (writes to PTY)
  │<──── output {data} ───────────│
  │                               │
  │──── interrupt ───────────────>│
  │                               │ (sends SIGINT)
  │                               │
  │<──── status {exited, 130} ────│
  │                               │
```

## Database Schema

### Projects Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR | Project name |
| description | VARCHAR | Optional description |
| github_url | VARCHAR | Repository URL |
| local_path | VARCHAR | File system path |
| container_id | VARCHAR | Associated container |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last modification |

## Deployment Considerations

### Development

```bash
docker compose up -d
# or run services separately
```

### Production

1. Build optimized images
2. Configure environment variables
3. Set up reverse proxy (nginx/traefik)
4. Configure SSL/TLS
5. Set appropriate CORS origins
6. Add authentication layer
7. Configure logging and monitoring

### Scaling

- Backend is stateless (except terminal sessions)
- Terminal sessions are memory-resident per instance
- Consider session affinity for WebSocket connections
- Database can be switched to PostgreSQL for scale

## Known Limitations

1. **No Authentication** - Currently open access
2. **Single Instance Terminal** - Sessions not distributed
3. **In-Memory Sessions** - Lost on restart
4. **SQLite** - Not suitable for high concurrency

## Future Enhancements

1. User authentication and authorization
2. Project templates and scaffolding
3. Multi-container workflows
4. Session persistence and replay
5. Collaborative terminal sharing
6. Resource quotas and limits
