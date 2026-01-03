# Phase 0: Setup

## What This Does
Spawns pre-flight agents to set up contracts, environment, and test fixtures.

## Execution Order
1. Contracts Agent + Environment Agent (parallel)
2. Wait for contracts to freeze
3. Fixture Agent (needs contracts)

---

## SPAWN: Contracts Agent

**Run in:** Main project directory
**Background:** No (need to wait for completion)

```
Read docs/agents/AGENT_CONTRACTS.md for your full instructions.

You are the Contracts Agent. Your job is to create the shared type definitions.

DO THIS NOW:
1. Create backend/app/models/contracts.py with Pydantic models:
   - ContainerStatus (enum)
   - Project, CreateProject
   - Container
   - TerminalMessage, TerminalCommand
   - Workflow, WorkflowStep, WorkflowExecution

2. Create frontend/src/lib/types/api.ts with matching TypeScript types

3. Create backend/tests/contracts/test_contracts.py with serialization tests

4. Run: pytest backend/tests/contracts/ -v

5. When done:
   bd create --title="Contracts: Shared types defined" --type=task --priority=0
   bd close <id> --tag=contracts-frozen
   bd sync

Signal completion by commenting: "Contracts frozen and validated"
```

---

## SPAWN: Environment Agent

**Run in:** Main project directory
**Background:** No (need to wait for completion)

```
Read docs/agents/AGENT_ENVIRONMENT.md for your full instructions.

You are the Environment Agent. Set up the development environment.

DO THIS NOW:
1. Create directory structure:
   mkdir -p backend/app/{models,routers,services,websockets}
   mkdir -p backend/tests/{contracts,integration,e2e}
   mkdir -p frontend/src/{routes,lib/{api,components,stores,types}}
   mkdir -p frontend/tests/{unit,e2e}
   mkdir -p frontend/static
   mkdir -p docker/claude-cli
   mkdir -p .github/workflows
   mkdir -p scripts

2. Create git worktrees:
   git worktree add ../tdd-backend -b backend
   git worktree add ../tdd-frontend -b frontend
   git worktree add ../tdd-infra -b infra

3. Create scripts/setup-worktrees.sh (executable)

4. Create scripts/verify-environment.sh (executable)

5. Create .editorconfig and .env.example

6. Run: ./scripts/verify-environment.sh

7. When done:
   bd create --title="Environment: Setup complete" --type=task --priority=0
   bd close <id> --tag=environment-ready
   bd sync
```

---

## SPAWN: Fixture Agent (after contracts frozen)

**Run in:** Main project directory
**Background:** No

```
Read docs/agents/AGENT_FIXTURE.md for your full instructions.

You are the Fixture Agent. Contracts are frozen - create test infrastructure.

DO THIS NOW:
1. Create backend/tests/conftest.py with fixtures:
   - sample_project, sample_container
   - mock_docker_client
   - mock_pty_process
   - async_mock_websocket

2. Create backend/tests/fixtures/projects.py with test data

3. Create docker/claude-cli/mock-claude.sh:
   - Handle STREAM, DELAY:N, ERROR, HANG, EXIT commands
   - Make executable

4. Create frontend/tests/fixtures/api-mocks.ts

5. Create frontend/tests/fixtures/websocket-mock.ts

6. Test:
   python -c "from backend.tests.conftest import *"
   echo "STREAM" | docker/claude-cli/mock-claude.sh

7. When done:
   bd create --title="Fixtures: Test infrastructure ready" --type=task --priority=0
   bd close <id> --tag=fixtures-ready
   bd sync
```

---

## Completion Check

Before moving to Phase 1, verify:
```bash
bd list --tag=contracts-frozen   # Should show 1
bd list --tag=environment-ready  # Should show 1
bd list --tag=fixtures-ready     # Should show 1
git worktree list                # Should show 3 worktrees
```
