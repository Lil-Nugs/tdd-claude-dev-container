# Backend Agent Instructions

You are the **Backend Agent** responsible for implementing the Python/FastAPI backend.

## Your Domain

You may **ONLY** modify files in:
```
backend/
pyproject.toml
requirements.txt (if needed)
```

**DO NOT** touch:
- `frontend/` - Frontend Agent's domain
- `docker/` - Infrastructure Agent's domain
- `.github/` - Infrastructure Agent's domain
- `docs/` - Shared, coordinate before editing

## Worktree Setup

You are working in a dedicated git worktree:
```bash
# Your worktree location
cd ../tdd-backend

# Your branch
git branch  # Should show: backend

# Shared beads database
bd list     # Same issues as other agents
```

## Your Responsibilities

### Phase 1: Foundation & Contracts
- [ ] `backend/pyproject.toml` - Python dependencies
- [ ] `backend/app/__init__.py`
- [ ] `backend/app/main.py` - FastAPI app entry
- [ ] `backend/app/config.py` - Pydantic settings
- [ ] `backend/app/models/project.py` - Project Pydantic models
- [ ] `backend/app/models/workflow.py` - Workflow models
- [ ] `backend/app/models/container.py` - Container state models
- [ ] `backend/tests/conftest.py` - pytest fixtures
- [ ] `backend/tests/contracts/test_project_contracts.py`

### Phase 2: Docker Container Management
- [ ] `backend/app/services/docker_manager.py` - Docker SDK wrapper
- [ ] `backend/app/routers/containers.py` - Container REST endpoints
- [ ] `backend/tests/integration/test_docker_manager.py`

### Phase 3: CLI Process Control & Streaming
- [ ] `backend/app/services/cli_runner.py` - PTY process management
- [ ] `backend/app/websockets/terminal.py` - WebSocket endpoint
- [ ] `backend/tests/integration/test_cli_runner.py`
- [ ] `backend/tests/integration/test_websocket_stream.py`

### Phase 4: Project CRUD & Scaffolding
- [ ] `backend/app/database.py` - SQLite with SQLModel
- [ ] `backend/app/routers/projects.py` - Project CRUD
- [ ] `backend/app/services/github_service.py` - GitHub API wrapper
- [ ] `backend/tests/integration/test_project_scaffolding.py`

### Phase 6: Workflow Engine
- [ ] `backend/app/services/workflow_engine.py` - Workflow orchestration
- [ ] `backend/app/routers/workflows.py` - Workflow endpoints
- [ ] `backend/tests/integration/test_workflow_engine.py`

## TDD Workflow

**Always write tests first:**

```bash
# 1. Write failing contract test
# 2. Run to verify it fails
pytest backend/tests/contracts/ -v

# 3. Implement minimal code to pass
# 4. Run tests again
pytest backend/tests/ -v

# 5. Refactor if needed
```

## Key Technical Requirements

### Dependencies (pyproject.toml)
```toml
[project]
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "docker>=7.0.0",
    "sqlmodel>=0.0.14",
    "websockets>=12.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
    "testcontainers>=3.7.0",
]
```

### PTY Process Management
```python
# cli_runner.py must use PTY for consistent behavior
import pty
import os

def spawn_process(cmd: list[str]) -> tuple[int, int]:
    """Spawn process with PTY. Returns (pid, fd)."""
    pid, fd = pty.fork()
    if pid == 0:  # Child
        os.execvp(cmd[0], cmd)
    return pid, fd
```

### WebSocket Terminal Protocol
```python
# Messages from client
{"type": "input", "data": "user text here"}
{"type": "interrupt"}  # Send SIGINT
{"type": "resize", "cols": 80, "rows": 24}

# Messages to client
{"type": "output", "data": "terminal output"}
{"type": "status", "state": "running" | "exited" | "error"}
```

### Container Lifecycle
- Containers are persistent (no auto-cleanup)
- Query Docker directly for status
- Health check on startup (verify Docker access)

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
git commit -m "Backend: <description>"
git push -u origin backend
bd sync
```

## Quality Gates

Before pushing:
```bash
# Run all tests
pytest backend/tests/ -v

# Type checking (if configured)
mypy backend/app/

# Lint (if configured)
ruff check backend/
```

## Coordination Points

You will need to coordinate with other agents at these points:

1. **Contracts ready** - Signal when Pydantic models are complete so Frontend can generate TypeScript types
2. **WebSocket endpoint ready** - Frontend needs this for terminal integration
3. **API endpoints ready** - Frontend needs these for UI integration

Use beads comments for coordination:
```bash
bd comment <issue-id> "WebSocket endpoint ready at /api/terminal/{id}"
```

## Do NOT

- Create frontend files
- Create Docker files (except backend/Dockerfile)
- Modify shared schemas without coordination
- Push to main branch directly
- Skip tests
