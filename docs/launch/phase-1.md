# Phase 1: Implementation

## What This Does
Spawns domain agents to implement backend, frontend, and infrastructure in parallel.
Also spawns a watchdog to monitor progress.

## Prerequisites
Phase 0 must be complete:
```bash
bd list --tag=contracts-frozen   # ✓
bd list --tag=fixtures-ready     # ✓
git worktree list                # Shows 3 worktrees
```

---

## SPAWN: All Implementation Agents (Parallel)

Spawn these 4 agents simultaneously using parallel Task calls:

### Agent 1: Backend Agent

**Run in:** ../tdd-backend (worktree)
**Background:** Yes

```
Read docs/agents/AGENT_BACKEND.md for your full instructions.

You are the Backend Agent working in the backend worktree.

SETUP:
cd ../tdd-backend
git branch  # Verify: backend

DO THIS NOW (TDD - tests first for each):

1. Create backend/pyproject.toml with dependencies

2. Create backend/app/main.py - FastAPI app with health endpoint

3. Create backend/app/config.py - Pydantic settings

4. Create backend/app/services/docker_manager.py - Docker SDK wrapper
   - Tests in backend/tests/integration/test_docker_manager.py

5. Create backend/app/services/cli_runner.py - PTY process management
   - Tests in backend/tests/integration/test_cli_runner.py

6. Create backend/app/websockets/terminal.py - WebSocket endpoint
   - Tests in backend/tests/integration/test_websocket_stream.py

7. Create backend/app/routers/projects.py - Project CRUD
8. Create backend/app/routers/containers.py - Container endpoints
9. Create backend/app/database.py - SQLite with SQLModel

After each feature:
bd update <id> --status=in_progress  # When starting
bd close <id> && bd sync              # When done

COMPLETION:
pytest backend/tests/ -v
git add . && git commit -m "Backend: Complete implementation"
git push -u origin backend
bd sync
```

### Agent 2: Frontend Agent

**Run in:** ../tdd-frontend (worktree)
**Background:** Yes

```
Read docs/agents/AGENT_FRONTEND.md for your full instructions.

You are the Frontend Agent working in the frontend worktree.

SETUP:
cd ../tdd-frontend
git branch  # Verify: frontend

DO THIS NOW:

1. Create frontend/package.json with dependencies
2. Create frontend/svelte.config.js
3. Create frontend/vite.config.ts
4. Create frontend/tsconfig.json

5. Create frontend/src/app.html
6. Create frontend/src/routes/+layout.svelte
7. Create frontend/src/routes/+page.svelte - Dashboard

8. Create frontend/src/lib/components/Terminal.svelte - xterm.js wrapper
   - Include data-testid attributes
   - Handle cleanup in onDestroy

9. Create frontend/src/lib/components/ProjectCard.svelte

10. Create frontend/src/lib/api/client.ts - REST client
11. Create frontend/src/lib/api/websocket.ts - WebSocket handler

12. Create frontend/static/manifest.json - PWA manifest

13. Create frontend/src/routes/projects/+page.svelte
14. Create frontend/src/routes/projects/[id]/+page.svelte
15. Create frontend/src/routes/projects/[id]/terminal/+page.svelte

COMPLETION:
npm run check
npm run build
git add . && git commit -m "Frontend: Complete implementation"
git push -u origin frontend
bd sync
```

### Agent 3: Infrastructure Agent

**Run in:** ../tdd-infra (worktree)
**Background:** Yes

```
Read docs/agents/AGENT_INFRA.md for your full instructions.

You are the Infrastructure Agent working in the infra worktree.

SETUP:
cd ../tdd-infra
git branch  # Verify: infra

DO THIS NOW:

1. Create docker/claude-cli/Dockerfile
   - Ubuntu 22.04 base
   - Node, Python, git
   - Non-root user

2. Create docker/claude-cli/entrypoint.sh

3. Create docker-compose.yml
   - backend service
   - frontend service
   - claude-test service

4. Create .github/workflows/ci.yml
   - contracts job
   - integration job (depends on contracts)
   - frontend job
   - e2e job (depends on integration + frontend)

5. Create .github/dependabot.yml

6. Create Makefile with targets:
   - help, setup, test, build, dev, clean

7. Create scripts/test-all.sh

COMPLETION:
docker compose build
git add . && git commit -m "Infra: Complete implementation"
git push -u origin infra
bd sync
```

### Agent 4: Watchdog Agent

**Run in:** Main project directory
**Background:** Yes

```
Read docs/agents/AGENT_WATCHDOG.md for your full instructions.

You are the Watchdog Agent. Monitor the other agents.

DO THIS NOW (loop until other agents complete):

Every 5 minutes:
1. Check bd list --status=in_progress for stale issues (>30 min)
2. Check git branches for recent commits
3. Watch for domain violations (wrong files touched)
4. Check bd sync --status for conflicts

If problems found:
bd create --title="Watchdog: <problem>" --type=bug --priority=1

Post progress update:
bd comment <watchdog-issue> "Status: Backend X/Y, Frontend X/Y, Infra X/Y"

Complete when all domain agents finish.
```

---

## Monitor Progress

```bash
/tasks                           # Check agent status
bd stats                         # Overall progress
bd list --status=in_progress     # Active work
git fetch --all && git log --oneline --graph --all -10
```

---

## Completion Check

Before moving to Phase 2:
```bash
# All agents finished
/tasks  # No running agents

# All branches have commits
git log origin/backend --oneline -1
git log origin/frontend --oneline -1
git log origin/infra --oneline -1

# Beads synced
bd sync
bd stats
```
