# Phase 3: Integration

## What This Does
Merges all branches to main and runs full E2E validation.

## Prerequisites
Phase 2 must be complete with no blockers:
```bash
bd list --tag=reviewed            # 3 results
bd list --priority=0 --status=open  # 0 results
bd list --priority=1 --status=open  # 0 results
```

---

## SPAWN: Merge Agent

**Run in:** Main project directory
**Background:** No (sequential, need to wait)

```
Read docs/agents/AGENT_MERGE.md for your full instructions.

You are the Merge Agent. Merge all implementation branches.

DO THIS NOW:

1. PREPARE:
   cd /home/mattc/projects/tdd-claude-dev-container
   git checkout main
   git pull origin main
   git fetch --all

2. MERGE INFRA (first - others depend on it):
   git merge origin/infra --no-ff -m "Merge infrastructure implementation

   Includes:
   - Docker base image and mock-claude
   - docker-compose.yml
   - CI/CD pipeline
   - Development scripts

   Reviewed-by: Infra Review Agent"

   # Verify
   docker compose build

3. MERGE BACKEND:
   git merge origin/backend --no-ff -m "Merge backend implementation

   Includes:
   - FastAPI application
   - Docker manager service
   - PTY CLI runner
   - WebSocket terminal
   - Project CRUD

   Reviewed-by: Backend Review Agent"

   # Verify
   pytest backend/tests/contracts/ -v

4. MERGE FRONTEND:
   git merge origin/frontend --no-ff -m "Merge frontend implementation

   Includes:
   - SvelteKit PWA
   - Terminal component
   - Project dashboard
   - WebSocket integration

   Reviewed-by: Frontend Review Agent"

   # Verify
   cd frontend && npm run check

5. CONFLICT RESOLUTION (if any):
   - backend/** → Accept backend version
   - frontend/** → Accept frontend version
   - docker/** → Accept infra version
   - Shared files → Create issue for review

6. SYNC AND PUSH:
   bd sync
   git push origin main

COMPLETION:
bd create --title="Merge: All branches integrated" --type=task --priority=1
bd close <id> --tag=merge-complete
bd sync
```

---

## SPAWN: Integration Review Agent

**Run in:** Main project directory
**Background:** No

```
Read docs/agents/AGENT_REVIEW_INTEGRATION.md for your full instructions.

You are the Integration Review Agent. Verify everything works together.

DO THIS NOW:

1. START FULL STACK:
   docker compose up -d
   sleep 10
   docker compose ps  # All healthy?

2. HEALTH CHECK:
   curl http://localhost:8000/api/health
   curl http://localhost:5173

3. E2E TESTS:
   cd frontend
   npx playwright install --with-deps
   npm run test:e2e

4. MANUAL FLOW TEST:
   - Open http://localhost:5173
   - Create a project
   - Start its container
   - Open terminal
   - Type a command
   - Verify output appears
   - Close terminal
   - Stop container

5. ERROR HANDLING TEST:
   - Stop backend: docker compose stop backend
   - Verify frontend shows connection error
   - Restart: docker compose start backend
   - Verify reconnection

6. CONTRACT ALIGNMENT:
   - Compare backend/app/models/contracts.py
   - With frontend/src/lib/types/api.ts
   - All fields match?

For each issue found:
bd create --title="Integration: <issue>" --type=bug --priority=<0-4>

COMPLETION:
docker compose down
Post summary with E2E results
bd create --title="Integration: Review complete" --type=task --priority=1
bd close <id> --tag=integration-complete
bd sync
```

---

## Integration Gates

Before proceeding to Phase 4:
```bash
bd list --tag=merge-complete        # 1 result
bd list --tag=integration-complete  # 1 result

# E2E tests should pass
# No P0/P1 issues from integration review
```
