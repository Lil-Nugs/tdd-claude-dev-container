# Parallel Agent Spawn Guide

This guide provides detailed instructions for spawning parallel agents with a comprehensive review workflow.

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PHASE 0: SETUP                                │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐                    │
│  │  Contracts  │  │ Environment  │  │  Fixtures   │                    │
│  │   Agent     │  │    Agent     │  │   Agent     │                    │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘                    │
│         │                │                  │                           │
│         └────────────────┼──────────────────┘                           │
│                          ▼                                              │
│                   Contracts Frozen                                      │
└─────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PHASE 1: IMPLEMENTATION                             │
│                                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Backend    │  │  Frontend    │  │    Infra    │  │  Watchdog   │   │
│  │   Agent     │  │    Agent     │  │    Agent    │  │   Agent     │   │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘  └─────────────┘   │
│         │                │                  │           (monitoring)    │
└─────────┼────────────────┼──────────────────┼───────────────────────────┘
          │                │                  │
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: REVIEW                                  │
│                                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐                    │
│  │  Backend    │  │  Frontend    │  │    Infra    │                    │
│  │  Review     │  │   Review     │  │   Review    │                    │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘                    │
│         │                │                  │                           │
│         └────────────────┼──────────────────┘                           │
│                          ▼                                              │
│                   All Reviews Pass                                      │
└─────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PHASE 3: INTEGRATION                               │
│                                                                         │
│  ┌─────────────┐                    ┌──────────────┐                   │
│  │   Merge     │ ──────────────────▶│ Integration  │                   │
│  │   Agent     │                    │   Review     │                   │
│  └─────────────┘                    └──────────────┘                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       PHASE 4: SIGN-OFF                                 │
│                                                                         │
│                      ┌──────────────┐                                   │
│                      │Documentation │                                   │
│                      │    Agent     │                                   │
│                      └──────────────┘                                   │
│                                                                         │
│                           ✅ RELEASE                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Agent Reference

| Agent | Phase | Doc | Purpose |
|-------|-------|-----|---------|
| Contracts | 0 | [AGENT_CONTRACTS.md](agents/AGENT_CONTRACTS.md) | Define shared types |
| Environment | 0 | [AGENT_ENVIRONMENT.md](agents/AGENT_ENVIRONMENT.md) | Setup worktrees, configs |
| Fixture | 0 | [AGENT_FIXTURE.md](agents/AGENT_FIXTURE.md) | Create test infrastructure |
| Backend | 1 | [AGENT_BACKEND.md](agents/AGENT_BACKEND.md) | Implement FastAPI backend |
| Frontend | 1 | [AGENT_FRONTEND.md](agents/AGENT_FRONTEND.md) | Implement SvelteKit PWA |
| Infra | 1 | [AGENT_INFRA.md](agents/AGENT_INFRA.md) | Docker, CI/CD, tooling |
| Watchdog | 1 | [AGENT_WATCHDOG.md](agents/AGENT_WATCHDOG.md) | Monitor progress |
| Backend Review | 2 | [AGENT_REVIEW_BACKEND.md](agents/AGENT_REVIEW_BACKEND.md) | Review backend code |
| Frontend Review | 2 | [AGENT_REVIEW_FRONTEND.md](agents/AGENT_REVIEW_FRONTEND.md) | Review frontend code |
| Infra Review | 2 | [AGENT_REVIEW_INFRA.md](agents/AGENT_REVIEW_INFRA.md) | Review infra code |
| Merge | 3 | [AGENT_MERGE.md](agents/AGENT_MERGE.md) | Merge branches |
| Integration Review | 3 | [AGENT_REVIEW_INTEGRATION.md](agents/AGENT_REVIEW_INTEGRATION.md) | E2E validation |
| Documentation | 4 | [AGENT_DOCUMENTATION.md](agents/AGENT_DOCUMENTATION.md) | Update docs |

---

## Phase 0: Setup

This phase MUST complete before spawning implementation agents.

### Step 0.1: Prerequisites

```bash
# Ensure you're in the main project directory
cd /home/mattc/projects/tdd-claude-dev-container

# Configure beads sync
bd config set sync.branch beads-sync

# Push current state
git push origin main
```

### Step 0.2: Spawn Pre-Flight Agents

Spawn Contracts and Environment agents in parallel:

```
Spawn two parallel agents for Phase 0 setup:

### Agent 1: Contracts Agent
"""
You are the Contracts Agent. Read docs/agents/AGENT_CONTRACTS.md for full instructions.

Create shared type definitions that all agents will build against:
1. backend/app/models/contracts.py - Pydantic models
2. frontend/src/lib/types/api.ts - TypeScript types
3. backend/tests/contracts/test_contracts.py - Contract tests

Key types needed:
- Project, CreateProject
- Container, ContainerStatus
- TerminalMessage, TerminalCommand
- Workflow, WorkflowStep, WorkflowExecution

When complete:
- Run: pytest backend/tests/contracts/ -v
- Tag issue: bd close <id> --tag=contracts-frozen
- Comment: "Contracts frozen and validated"
"""

### Agent 2: Environment Agent
"""
You are the Environment Agent. Read docs/agents/AGENT_ENVIRONMENT.md for full instructions.

Set up the development environment:
1. Create directory structure
2. Create git worktrees (backend, frontend, infra)
3. Create setup and verification scripts
4. Create .editorconfig and .env.example

When complete:
- Run: ./scripts/verify-environment.sh
- Tag issue: bd close <id> --tag=environment-ready
"""
```

### Step 0.3: Wait for Contracts, Then Spawn Fixture Agent

After contracts are frozen:

```
Spawn the Fixture Agent to create test infrastructure:

"""
You are the Fixture Agent. Read docs/agents/AGENT_FIXTURE.md for full instructions.

Contracts are now frozen. Create shared test infrastructure:
1. backend/tests/conftest.py - pytest fixtures
2. backend/tests/fixtures/ - test data
3. docker/claude-cli/mock-claude.sh - mock CLI
4. frontend/tests/fixtures/ - frontend mocks

Use types from backend/app/models/contracts.py.

When complete:
- Verify fixtures are importable
- Test mock-claude.sh
- Tag issue: bd close <id> --tag=fixtures-ready
"""
```

---

## Phase 1: Parallel Implementation

Once Phase 0 completes, spawn all implementation agents.

### Step 1.1: Spawn Implementation Agents

```
Spawn four parallel agents for implementation:

### Agent 1: Backend Agent
"""
You are the Backend Agent. Read docs/agents/AGENT_BACKEND.md for full instructions.

SETUP:
1. cd to ../tdd-backend (your worktree)
2. Verify you're on the 'backend' branch
3. Run `bd list` to see available issues

WORK:
1. Use contracts from backend/app/models/contracts.py
2. Use fixtures from backend/tests/conftest.py
3. Implement with TDD (tests first):
   - FastAPI app and health endpoint
   - Docker manager service
   - PTY CLI runner
   - WebSocket terminal
   - Project CRUD

4. After each issue: `bd close <id> && bd sync`

COMPLETION:
1. Run: pytest backend/tests/ -v
2. Push: git push -u origin backend
3. Final: bd sync
"""

### Agent 2: Frontend Agent
"""
You are the Frontend Agent. Read docs/agents/AGENT_FRONTEND.md for full instructions.

SETUP:
1. cd to ../tdd-frontend (your worktree)
2. Verify you're on the 'frontend' branch

WORK:
1. Use types from frontend/src/lib/types/api.ts
2. Use fixtures from frontend/tests/fixtures/
3. Implement:
   - SvelteKit app structure
   - Terminal component (xterm.js)
   - Project dashboard
   - API client and WebSocket handler
   - PWA manifest and service worker

4. Add data-testid attributes for E2E testing
5. After each issue: `bd close <id> && bd sync`

COMPLETION:
1. Run: npm run check && npm run build
2. Push: git push -u origin frontend
3. Final: bd sync
"""

### Agent 3: Infrastructure Agent
"""
You are the Infrastructure Agent. Read docs/agents/AGENT_INFRA.md for full instructions.

SETUP:
1. cd to ../tdd-infra (your worktree)
2. Verify you're on the 'infra' branch

WORK:
1. Docker infrastructure:
   - docker/claude-cli/Dockerfile
   - docker-compose.yml

2. CI/CD:
   - .github/workflows/ci.yml
   - .github/dependabot.yml

3. Tooling:
   - Makefile
   - scripts/test-all.sh

4. After each issue: `bd close <id> && bd sync`

COMPLETION:
1. Run: docker compose build
2. Push: git push -u origin infra
3. Final: bd sync
"""

### Agent 4: Watchdog Agent (Background)
"""
You are the Watchdog Agent. Read docs/agents/AGENT_WATCHDOG.md for full instructions.

Run continuously while other agents work:
1. Monitor beads for stuck issues (>30 min no activity)
2. Check for domain violations (agents touching wrong files)
3. Watch for beads sync conflicts
4. Generate progress reports every 15 minutes
5. Alert if contracts are modified

Create issues for any problems detected.

Complete when all domain agents finish.
"""
```

### Step 1.2: Monitor Progress

While agents work:

```bash
# Check agent status
/tasks

# View beads progress
bd stats
bd list --status=in_progress

# Check git branches
git fetch --all
git log --oneline --graph --all -20
```

---

## Phase 2: Review

After implementation completes, spawn review agents.

### Step 2.1: Spawn Review Agents

```
Spawn three parallel review agents:

### Agent 1: Backend Review Agent
"""
You are the Backend Review Agent. Read docs/agents/AGENT_REVIEW_BACKEND.md for full instructions.

Review the backend implementation:
1. Run automated checks (pytest, mypy, ruff)
2. Check TDD compliance (>80% coverage)
3. Security audit (injection, path traversal)
4. Error handling review
5. Contract compliance

Create issues for findings with appropriate priority:
- P0-P1: Security, data loss risks
- P2: Functionality issues
- P3-P4: Code quality

Post summary comment when complete.
Tag: bd update <impl-issue> --tag=reviewed
"""

### Agent 2: Frontend Review Agent
"""
You are the Frontend Review Agent. Read docs/agents/AGENT_REVIEW_FRONTEND.md for full instructions.

Review the frontend implementation:
1. Run automated checks (tsc, build)
2. Type safety (no 'any' types)
3. Accessibility audit
4. XSS vulnerabilities
5. Contract compliance
6. Component quality (data-testid, cleanup)

Create issues for findings.
Post summary comment when complete.
Tag: bd update <impl-issue> --tag=reviewed
"""

### Agent 3: Infra Review Agent
"""
You are the Infra Review Agent. Read docs/agents/AGENT_REVIEW_INFRA.md for full instructions.

Review the infrastructure implementation:
1. Dockerfile security (non-root, pinned versions)
2. Docker Compose configuration
3. CI/CD pipeline (pinned actions, permissions)
4. Scripts quality (strict mode, quoting)
5. mock-claude.sh functionality

Create issues for findings.
Post summary comment when complete.
Tag: bd update <impl-issue> --tag=reviewed
"""
```

### Step 2.2: Review Gates

Reviews must pass before proceeding:

```bash
# Check all implementations are reviewed
bd list --tag=reviewed  # Should be 3

# Check for blocking issues
bd list --priority=0 --status=open  # Should be 0
bd list --priority=1 --status=open  # Should be 0 or approved
```

---

## Phase 3: Integration

After reviews pass, merge and validate.

### Step 3.1: Spawn Merge Agent

```
Spawn the Merge Agent:

"""
You are the Merge Agent. Read docs/agents/AGENT_MERGE.md for full instructions.

Prerequisites verified:
- All reviews complete (3 reviewed tags)
- No P0/P1 issues open

Merge branches in order:
1. git merge origin/infra --no-ff
2. git merge origin/backend --no-ff
3. git merge origin/frontend --no-ff

After each merge:
- Verify build: docker compose build
- Run contract tests: pytest backend/tests/contracts/ -v

Handle conflicts by domain ownership.
Push to main when all merged.
Sync beads: bd sync
"""
```

### Step 3.2: Spawn Integration Review Agent

After merge:

```
Spawn the Integration Review Agent:

"""
You are the Integration Review Agent. Read docs/agents/AGENT_REVIEW_INTEGRATION.md for full instructions.

All branches merged to main. Verify integration:

1. Start full stack: docker compose up -d
2. Run E2E tests: npm run test:e2e
3. Manual testing of core flows:
   - Create project
   - Start container
   - Open terminal
   - Send commands
   - Handle errors

4. Verify contract alignment (backend ↔ frontend)
5. Test error propagation

Create issues for integration problems.
Post summary with E2E results and recommendation.
"""
```

---

## Phase 4: Sign-Off

After integration passes, finalize documentation.

### Step 4.1: Spawn Documentation Agent

```
Spawn the Documentation Agent:

"""
You are the Documentation Agent. Read docs/agents/AGENT_DOCUMENTATION.md for full instructions.

Integration complete. Update documentation:

1. README.md - Quick start, features, structure
2. docs/api/ - API documentation
3. docs/architecture/ - System design
4. docs/contracts/ - Type documentation
5. docs/user-guide/ - End-user guide
6. CHANGELOG.md - Release notes

Verify all code examples work.
Check for broken links.

Signal release readiness when complete.
"""
```

---

## Quick Reference

### Spawn Commands Summary

```bash
# Phase 0: Setup (sequential start, then parallel)
# 1. Contracts + Environment in parallel
# 2. Fixtures (after contracts frozen)

# Phase 1: Implementation (all parallel)
# Backend + Frontend + Infra + Watchdog

# Phase 2: Review (all parallel)
# Backend Review + Frontend Review + Infra Review

# Phase 3: Integration (sequential)
# Merge → Integration Review

# Phase 4: Sign-off
# Documentation
```

### Beads Tags Reference

| Tag | Meaning |
|-----|---------|
| `contracts-frozen` | Contracts finalized, don't modify |
| `environment-ready` | Worktrees and configs ready |
| `fixtures-ready` | Test infrastructure ready |
| `reviewed` | Code review complete |
| `review-complete` | Review agent finished |
| `merge-complete` | Branches merged |
| `integration-complete` | E2E validation passed |
| `docs-complete` | Documentation updated |

### Emergency Commands

```bash
# Check what's stuck
bd list --status=in_progress

# Kill a hung agent
/tasks
# Use TaskOutput or kill

# Abort merge
git merge --abort

# Revert bad merge
git revert -m 1 HEAD

# Force beads sync
bd sync
```

---

## Expected Outcomes

After successful execution:

1. **Contracts**: Frozen, validated types in Python and TypeScript
2. **Backend**: FastAPI service with Docker, PTY, WebSocket
3. **Frontend**: SvelteKit PWA with terminal UI
4. **Infrastructure**: Docker, CI/CD, development tools
5. **Reviews**: All code reviewed, issues created for findings
6. **Integration**: Full stack tested, E2E passing
7. **Documentation**: Complete, accurate, release-ready

### Agent Execution Summary

| Phase | Agents | Parallel? | Blocking? |
|-------|--------|-----------|-----------|
| 0 | Contracts, Environment | Yes | Yes - must complete |
| 0 | Fixtures | No | Yes - after contracts |
| 1 | Backend, Frontend, Infra, Watchdog | Yes | Yes - all must complete |
| 2 | Backend/Frontend/Infra Review | Yes | Yes - all must pass |
| 3 | Merge | No | Yes |
| 3 | Integration Review | No | Yes - must pass |
| 4 | Documentation | No | No - release ready |

---

## Troubleshooting

### Agent Stuck
```bash
# Check status
/tasks
bd list --status=in_progress

# Watchdog should have created an issue
bd list --assignee=watchdog
```

### Review Found Critical Issues
```bash
# Check P0/P1 issues
bd list --priority=0 --status=open
bd list --priority=1 --status=open

# Must be fixed before merge
# Spawn fix agent or have implementation agent address
```

### Integration Tests Failing
```bash
# Check docker status
docker compose ps
docker compose logs

# Re-run specific test
cd frontend && npx playwright test tests/e2e/<test>.spec.ts
```

### Merge Conflicts
```bash
# See AGENT_MERGE.md for resolution guidelines
# Generally: domain owner wins
# For shared files: create issue for review
```
