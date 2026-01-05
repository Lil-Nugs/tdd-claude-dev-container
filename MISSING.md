# Missing Features for Project Completion

This document lists what's needed to complete the TDD Claude Dev Container project. Each item can be tackled independently in a session.

---

## Priority 1: Core Missing Features

### 1.1 Workflow Engine (Backend)

**Status:** Contracts defined, no implementation

The workflow system is defined in `backend/app/models/contracts.py` with:
- `Workflow` - template with steps
- `WorkflowStep` - individual step with command, timeout, review flag
- `WorkflowExecution` - running/completed execution state
- `WorkflowStatus` enum - pending, running, paused, completed, failed, cancelled

**Needed:**
- [ ] Create `backend/app/routers/workflows.py` with CRUD endpoints
- [ ] Create `backend/app/models/workflow.py` SQLModel for database persistence
- [ ] Create `backend/app/services/workflow_executor.py` to run workflows
- [ ] Add database migrations for workflow tables
- [ ] Integration tests for workflow execution

**Frontend types already exist:** `frontend/src/lib/types/api.ts` has matching TypeScript interfaces.

---

### 1.2 Workflow UI (Frontend)

**Status:** Not started

**Needed:**
- [ ] Create `/routes/workflows/+page.svelte` - list/create workflows
- [ ] Create `/routes/workflows/[id]/+page.svelte` - workflow detail/edit
- [ ] Create `/routes/projects/[id]/workflows/+page.svelte` - run workflow on project
- [ ] Add workflow API client methods to `lib/api/client.ts`
- [ ] Create `lib/components/WorkflowEditor.svelte` - step builder UI
- [ ] Create `lib/components/WorkflowRunner.svelte` - execution monitor

---

## Priority 2: Production Readiness

### 2.1 Authentication System

**Status:** No auth exists

**Needed:**
- [ ] Choose auth strategy (JWT tokens vs session-based)
- [ ] Create `backend/app/routers/auth.py` - login/logout/register
- [ ] Create `backend/app/models/user.py` - User SQLModel
- [ ] Add auth middleware/dependencies
- [ ] Protect API endpoints
- [ ] Frontend login page and auth state management
- [ ] Secure WebSocket connections

---

### 2.2 CORS Configuration

**Status:** Wildcard `["*"]` in `backend/app/main.py:45`

**Needed:**
- [ ] Move allowed origins to `backend/app/config.py`
- [ ] Configure environment-specific origins (dev vs prod)
- [ ] Document CORS setup in deployment guide

---

### 2.3 Session Persistence

**Status:** Terminal sessions are in-memory only

**Needed:**
- [ ] Design session storage (Redis? SQLite? File-based?)
- [ ] Persist terminal output history
- [ ] Implement session reconnection
- [ ] Add session replay capability

---

## Priority 3: PWA Features

### 3.1 Service Worker

**Status:** Missing entirely

**Needed:**
- [ ] Create `frontend/src/service-worker.ts`
- [ ] Configure SvelteKit for service worker generation
- [ ] Implement offline caching strategy
- [ ] Handle background sync for offline actions

---

### 3.2 PWA Assets

**Status:** Icons missing from `frontend/static/`

**Needed:**
- [ ] Generate PWA icon set (192x192, 512x512, etc.)
- [ ] Create `frontend/static/manifest.json`
- [ ] Add apple-touch-icon variants
- [ ] Configure theme colors

---

## Priority 4: Code Quality

### 4.1 Linting Fixes

**Status:** 20 fixable Ruff errors

**Needed:**
- [ ] Run `ruff check --fix backend/`
- [ ] Review and commit changes

---

### 4.2 Shell Script Fixes

**Status:** Unquoted variables in scripts

**Files:**
- [ ] `scripts/verify-environment.sh` - unquoted variable
- [ ] `scripts/setup-worktrees.sh` - unquoted variable

---

### 4.3 Frontend CSS Fixes

**Status:** Terminal component missing status classes

**File:** `frontend/src/lib/components/Terminal.svelte`

**Needed:**
- [ ] Add CSS for `.status-exited` class
- [ ] Add CSS for `.status-error` class

---

## Priority 5: Cleanup Stale Issues

The following beads issues appear to be stale (files exist):

```
tdd-claude-dev-container-640 - Missing Makefile (EXISTS: /Makefile)
tdd-claude-dev-container-ow7 - Missing CI/CD (EXISTS: /.github/workflows/ci.yml)
tdd-claude-dev-container-cco - Missing docker-compose.yml (EXISTS: /docker-compose.yml)
tdd-claude-dev-container-pib - Missing Dockerfile (EXISTS: backend/, frontend/, docker/claude-cli/)
tdd-claude-dev-container-bjk - Missing contracts.py (EXISTS: backend/app/models/contracts.py)
```

**Needed:**
- [ ] Review each issue
- [ ] Close if resolved: `bd close <id> --reason="File exists"`

---

## Quick Reference: File Locations

| Component | Location |
|-----------|----------|
| Backend contracts | `backend/app/models/contracts.py` |
| Frontend types | `frontend/src/lib/types/api.ts` |
| Backend routers | `backend/app/routers/` |
| Frontend routes | `frontend/src/routes/` |
| Backend services | `backend/app/services/` |
| Frontend components | `frontend/src/lib/components/` |
| Backend tests | `backend/tests/` |
| Config | `backend/app/config.py` |

---

## Suggested Session Order

1. **Session 1:** Close stale beads issues, fix linting/shell scripts (quick wins)
2. **Session 2:** Implement workflow backend (router + service + tests)
3. **Session 3:** Implement workflow frontend (pages + components)
4. **Session 4:** Add authentication system
5. **Session 5:** PWA features (service worker + assets)
6. **Session 6:** Session persistence + CORS hardening
