# Claude Code Remote Control PWA - Design

## Overview

PWA to remotely control Claude Code CLI instances in Docker containers on a home minipc.

## Core Features

1. **Project Scaffolding** - Create projects with git, GitHub repo, beads init
2. **Workflow Execution** - Run beads workflows with Claude self-review, loopable
3. **Live Observation** - Stream CLI output with interrupt/redirect capability
4. **Container Isolation** - Persistent container per project, sequential execution

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Frontend | SvelteKit | Lightweight, built-in PWA |
| Backend | Python + FastAPI | Good Docker SDK, async WebSockets |
| Containers | Docker Socket | Direct API, full lifecycle control |
| Database | SQLite | Simple, projects on disk |
| Real-time | WebSockets | Streaming CLI output |
| Project Path | Configurable | `PROJECTS_ROOT` env var, default `~/projects` |

## Key Architecture Decisions

### Container Lifecycle
- **Persistent containers** - stay running until user resets or system restarts
- **Explicit reset/recreate action** available via API
- **No automatic cleanup**

### Process Execution
- **PTY for everything** - consistent behavior (colors, line editing, Ctrl+C)
- **Ready detection** - wait for output pattern before sending input

### WebSocket Behavior
- **Broadcast to all connections** - multiple tabs see same output (like tmux attach)
- **Reconnect = full refresh** - server sends last N lines, client replaces content
- **No sequence numbers** - TCP guarantees ordering

### Workflow Orchestration
- **Prompt-driven** - Claude decides when steps complete via sub-agents
- **Max 5 review iterations** - then escalate or proceed
- **Clarification requests** - spawn sub-agent to attempt answering before user escalation

### Auth/Security
- **No auth for v1** - home network assumed trusted
- **Output buffer cap: 10MB** - prevent memory bloat

---

## Project Structure

```
tdd-claude-dev-container/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Settings/env vars
│   │   ├── database.py             # SQLite setup
│   │   ├── models/
│   │   │   ├── project.py          # Project Pydantic models
│   │   │   ├── workflow.py         # Workflow models
│   │   │   └── container.py        # Container state models
│   │   ├── routers/
│   │   │   ├── projects.py         # /api/projects endpoints
│   │   │   ├── workflows.py        # /api/workflows endpoints
│   │   │   └── containers.py       # /api/containers endpoints
│   │   ├── services/
│   │   │   ├── docker_manager.py   # Docker SDK wrapper
│   │   │   ├── cli_runner.py       # PTY process management
│   │   │   ├── workflow_engine.py  # Workflow orchestration
│   │   │   └── github_service.py   # GitHub repo creation
│   │   └── websockets/
│   │       └── terminal.py         # WebSocket terminal stream
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── contracts/              # Fast schema tests
│   │   ├── integration/            # Docker tests
│   │   └── e2e/                    # Full backend E2E
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte
│   │   │   ├── +page.svelte        # Dashboard/project list
│   │   │   ├── projects/
│   │   │   │   ├── +page.svelte
│   │   │   │   └── [id]/
│   │   │   │       ├── +page.svelte
│   │   │   │       └── terminal/+page.svelte
│   │   │   └── workflows/+page.svelte
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── client.ts
│   │   │   │   └── websocket.ts
│   │   │   ├── components/
│   │   │   │   ├── Terminal.svelte
│   │   │   │   ├── ProjectCard.svelte
│   │   │   │   └── WorkflowRunner.svelte
│   │   │   └── stores/
│   │   ├── service-worker.ts
│   │   └── app.html
│   ├── static/manifest.json
│   ├── tests/
│   │   ├── unit/
│   │   └── e2e/
│   ├── svelte.config.js
│   ├── vite.config.ts
│   └── package.json
├── docker/
│   ├── claude-cli/
│   │   ├── Dockerfile              # Base image with Claude CLI
│   │   └── mock-claude.sh          # Mock for testing
│   └── docker-compose.yml
└── shared/
    └── schemas/api.json            # OpenAPI schema (generated)
```

---

## Implementation Phases

### Phase 1: Foundation & Contracts

**Goal**: Project structure, API contracts, test infrastructure.

**Files**:
- `backend/pyproject.toml` - Python deps (fastapi, pydantic, docker, pytest, testcontainers)
- `backend/app/main.py` - FastAPI app with health endpoint
- `backend/app/config.py` - Pydantic settings
- `backend/app/models/project.py` - Project model contracts
- `backend/tests/conftest.py` - pytest fixtures
- `backend/tests/contracts/test_project_contracts.py`

**Tests first**:
1. Contract tests for Project model shape
2. Contract tests for `/api/health` endpoint
3. Implement to pass

**Deliverable**: Passing contract tests, OpenAPI schema

---

### Phase 2: Docker Container Management

**Goal**: Manage container lifecycle via Docker SDK.

**Files**:
- `docker/claude-cli/Dockerfile` - Base image (Ubuntu + Node + Claude CLI)
- `docker/claude-cli/mock-claude.sh` - Mock for CI testing
- `backend/app/services/docker_manager.py` - Container CRUD
- `backend/app/routers/containers.py` - REST endpoints
- `backend/app/models/container.py` - State models
- `backend/tests/integration/test_docker_manager.py`

**Key behaviors**:
- **Startup health check** - verify Docker access, fail fast with actionable errors
- Use Docker's native states (no custom state machine)
- Query Docker directly for container status

**Tests first**:
1. Create container, verify running, stop, remove
2. List containers, filter by project
3. Container death detection

**Deliverable**: Create/start/stop/remove containers via API

---

### Phase 3: CLI Process Control & Streaming

**Goal**: Run Claude CLI in containers, stream output via WebSocket.

**Files**:
- `backend/app/services/cli_runner.py` - PTY process management
- `backend/app/websockets/terminal.py` - WebSocket endpoint
- `backend/tests/integration/test_cli_runner.py`
- `backend/tests/integration/test_websocket_stream.py`

**Key behaviors**:
- CLI runs with `--dangerously-skip-permissions`
- **PTY for all processes** - consistent handling
- **Wait for output pattern** before sending input (ready detection)
- Output streamed real-time
- `interrupt` command sends SIGINT
- `input` command sends user text
- **Reconnect = full terminal refresh** (last N lines)

**Tests first**:
1. Spawn CLI process, capture stdout
2. WebSocket connects, receives stream
3. Send interrupt signal, process stops
4. Reconnect after drop, receive buffer

**Deliverable**: WebSocket streams CLI output, accepts input/interrupt

---

### Phase 4: Project CRUD & Scaffolding

**Goal**: Create/manage projects, scaffold with git/GitHub/beads.

**Files**:
- `backend/app/database.py` - SQLite with SQLModel
- `backend/app/routers/projects.py` - Project CRUD
- `backend/app/services/github_service.py` - GitHub API (gh CLI)
- `backend/tests/integration/test_project_scaffolding.py`

**Scaffolding workflow**:
1. Create directory at `$PROJECTS_ROOT/{name}`
2. `git init`
3. `gh repo create {name} --private --source=.`
4. `bd init`
5. Create initial files

**gh CLI error handling**:
- Not found → "Install GitHub CLI: https://cli.github.com"
- Auth error → "Run `gh auth login`"
- Repo exists → "Repo already exists, link instead?"
- Other → Show raw error

**Tests first**:
1. Project CRUD endpoint contracts
2. Create project creates directory
3. Scaffold initializes git
4. GitHub creation (mocked)
5. Rollback on failure

**Deliverable**: POST /api/projects scaffolds full project

---

### Phase 5: PWA Frontend - Core UI

**Goal**: SvelteKit PWA with project list, terminal view.

**Files**:
- `frontend/package.json` - Deps (svelte, @sveltejs/kit, xterm.js)
- `frontend/svelte.config.js`
- `frontend/vite.config.ts` - Vite + PWA plugin
- `frontend/src/routes/+layout.svelte`
- `frontend/src/routes/+page.svelte` - Dashboard
- `frontend/src/lib/components/Terminal.svelte` - xterm.js wrapper
- `frontend/src/lib/api/client.ts`
- `frontend/src/lib/api/websocket.ts`
- `frontend/static/manifest.json`
- `frontend/tests/e2e/projects.spec.ts`

**Key behaviors**:
- **Process status in UI** - `data-testid="process-status"` showing `running`/`exited`/`error`
- **E2E tests assert status element**, not terminal output parsing

**Tests first**:
1. Load dashboard, see project list
2. Click project, see terminal view
3. Terminal shows streamed output
4. Send interrupt command

**Deliverable**: PWA shows projects, connects to WebSocket

---

### Phase 6: Workflow Engine

**Goal**: Define and execute beads workflows with looping.

**Files**:
- `backend/app/models/workflow.py`
- `backend/app/services/workflow_engine.py`
- `backend/app/routers/workflows.py`
- `backend/tests/integration/test_workflow_engine.py`

**Workflow schema**:
```python
class WorkflowStep(BaseModel):
    name: str
    command: str  # e.g., "bd ready", "bd update {issue} --status in_progress"
    review_after: bool = False

class Workflow(BaseModel):
    name: str
    steps: list[WorkflowStep]
    loop_count: int = 1
```

**Built-in workflows**:
1. `beads-work-cycle`: pull ready issue → implement → self-review → close → repeat
2. `scaffold-project`: create dir → git → github → beads → initial commit

**Self-review mechanism**:
- Injects review prompt
- **Prompt-driven completion** - Claude/sub-agents decide when done
- **Max 5 iterations** then proceed
- **Clarification handling** - spawn sub-agent to attempt answering

**Tests first**:
1. Execute single-step workflow
2. Execute multi-step with loop
3. Review step triggers

**Deliverable**: POST /api/workflows/execute runs workflow

---

### Phase 7: Frontend Workflow UI

**Goal**: UI to trigger workflows, monitor progress.

**Files**:
- `frontend/src/routes/workflows/+page.svelte`
- `frontend/src/lib/components/WorkflowRunner.svelte`
- `frontend/src/lib/stores/workflow.ts`
- `frontend/tests/e2e/workflows.spec.ts`

**UI features**:
- Select project
- Select workflow template
- Set loop count
- Start/stop workflow
- Progress indicator

**Deliverable**: Full workflow control from PWA

---

### Phase 8: Polish & Offline Support

**Goal**: Service worker, error handling.

**Files**:
- `frontend/src/service-worker.ts`
- Error boundaries in Svelte components
- Reconnection logic

**Offline behavior**:
- Cache project list for viewing
- Show "offline" indicator
- Commands require connection

**Deliverable**: PWA installable, offline viewing

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| GET | /api/projects | List projects |
| POST | /api/projects | Create project |
| GET | /api/projects/{id} | Get project |
| DELETE | /api/projects/{id} | Delete project |
| POST | /api/projects/{id}/scaffold | Scaffold project |
| GET | /api/containers | List containers |
| POST | /api/containers | Create container |
| POST | /api/containers/{id}/start | Start container |
| POST | /api/containers/{id}/stop | Stop container |
| POST | /api/containers/{id}/reset | Reset container |
| DELETE | /api/containers/{id} | Remove container |
| WS | /api/terminal/{container_id} | Terminal stream |
| GET | /api/workflows | List templates |
| POST | /api/workflows/execute | Execute workflow |
| POST | /api/workflows/{id}/stop | Stop workflow |

---

## Deferred to Sub-Agent System Design

When designing the prompt orchestration system, define:

1. **Signaling protocol** - how Claude signals step completion
2. **Iteration criteria** - how Claude decides pass/iterate/fail
3. **Failure handling** - escalation to user
4. **Clarification sub-agents** - when to spawn vs. ask user
