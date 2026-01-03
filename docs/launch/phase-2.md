# Phase 2: Review

## What This Does
Spawns review agents to check each domain's implementation for quality, security, and correctness.

## Prerequisites
Phase 1 must be complete:
```bash
git log origin/backend --oneline -1   # Has commits
git log origin/frontend --oneline -1  # Has commits
git log origin/infra --oneline -1     # Has commits
```

---

## SPAWN: All Review Agents (Parallel)

Spawn these 3 agents simultaneously:

### Agent 1: Backend Review Agent

**Run in:** Main project directory (read ../tdd-backend)
**Background:** Yes

```
Read docs/agents/AGENT_REVIEW_BACKEND.md for your full instructions.

You are the Backend Review Agent. Review the backend implementation.

DO THIS NOW:

1. AUTOMATED CHECKS:
   cd ../tdd-backend
   pytest backend/tests/ -v --cov=app --cov-report=term-missing
   mypy backend/app/ --ignore-missing-imports
   ruff check backend/app/

2. TDD COMPLIANCE:
   - Coverage >80%?
   - Tests for each feature?

3. SECURITY AUDIT:
   - Command injection in subprocess calls?
   - Path traversal in file operations?
   - SQL injection (if raw SQL)?
   - Input validation on all endpoints?

4. ERROR HANDLING:
   - Try/except for Docker, file I/O?
   - Proper HTTP status codes?
   - No stack traces to client?

5. CONTRACT COMPLIANCE:
   - All endpoints use Pydantic models from contracts.py?
   - Response formats match contracts?

For each issue found:
bd create --title="Review: <issue>" --type=bug --priority=<0-4>
bd comment <id> "Found in <file:line>: <details>"

COMPLETION:
Post summary comment on implementation issue
bd update <backend-impl-issue> --tag=reviewed
bd sync
```

### Agent 2: Frontend Review Agent

**Run in:** Main project directory (read ../tdd-frontend)
**Background:** Yes

```
Read docs/agents/AGENT_REVIEW_FRONTEND.md for your full instructions.

You are the Frontend Review Agent. Review the frontend implementation.

DO THIS NOW:

1. AUTOMATED CHECKS:
   cd ../tdd-frontend
   npm run check
   npm run build

2. TYPE SAFETY:
   - Any 'any' types? grep -rn ": any\|as any" src/
   - All props typed?

3. ACCESSIBILITY:
   - Alt text on images?
   - Labels on inputs?
   - Buttons not divs for click handlers?

4. SECURITY:
   - @html with user content?
   - Sensitive data in localStorage?

5. COMPONENT QUALITY:
   - data-testid on interactive elements?
   - Cleanup in onDestroy?
   - Error states handled?

6. CONTRACT COMPLIANCE:
   - Types in api.ts match backend contracts.py?

For each issue found:
bd create --title="Review: <issue>" --type=bug --priority=<0-4>

COMPLETION:
Post summary comment on implementation issue
bd update <frontend-impl-issue> --tag=reviewed
bd sync
```

### Agent 3: Infrastructure Review Agent

**Run in:** Main project directory (read ../tdd-infra)
**Background:** Yes

```
Read docs/agents/AGENT_REVIEW_INFRA.md for your full instructions.

You are the Infrastructure Review Agent. Review the infra implementation.

DO THIS NOW:

1. DOCKERFILE SECURITY:
   - Running as non-root?
   - Base images pinned (not :latest)?
   - No secrets in Dockerfile?

2. DOCKER COMPOSE:
   - Health checks defined?
   - Resource limits?
   - Volumes secure?

3. CI/CD SECURITY:
   - Actions pinned to SHA?
   - Minimal permissions?
   - Secrets not logged?

4. SCRIPTS:
   - set -euo pipefail?
   - Variables quoted?
   - Meaningful exit codes?

5. MOCK-CLAUDE:
   - All commands work?
   - SIGINT handled?
   - No injection vulnerabilities?

For each issue found:
bd create --title="Review: <issue>" --type=bug --priority=<0-4>

COMPLETION:
Post summary comment on implementation issue
bd update <infra-impl-issue> --tag=reviewed
bd sync
```

---

## Review Gates

Before proceeding to Phase 3, verify:

```bash
# All reviewed
bd list --tag=reviewed  # Should be 3

# No blocking issues
bd list --priority=0 --status=open  # Must be 0
bd list --priority=1 --status=open  # Must be 0 (or explicitly approved)
```

If P0/P1 issues exist, they must be fixed before merge:
```
Spawn a fix agent for <issue>:
"""
Fix the issue described in <beads-id>.
Read the issue details: bd show <id>
Implement the fix in the appropriate worktree.
Run tests.
Close the issue: bd close <id>
"""
```
