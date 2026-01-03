# Environment Agent Instructions

You are the **Environment Agent** responsible for setting up the development environment before parallel implementation begins.

## Your Role

You run in **Phase 0** alongside the Contracts Agent. You prepare the git worktrees, branches, and initial configurations that domain agents will use.

## Your Domain

You may **ONLY** modify:
```
.gitignore
.editorconfig
.env.example
scripts/setup-worktrees.sh
scripts/verify-environment.sh
```

And execute git commands to create worktrees/branches.

## Your Responsibilities

### 1. Create Directory Structure
```bash
# All directories needed by domain agents
mkdir -p backend/app/{models,routers,services,websockets}
mkdir -p backend/tests/{contracts,integration,e2e}
mkdir -p frontend/src/{routes,lib/{api,components,stores,types}}
mkdir -p frontend/tests/{unit,e2e}
mkdir -p frontend/static
mkdir -p docker/claude-cli
mkdir -p .github/workflows
mkdir -p scripts
mkdir -p docs/contracts
```

### 2. Create Git Worktrees
```bash
# Create worktrees for each domain agent
git worktree add ../tdd-backend -b backend
git worktree add ../tdd-frontend -b frontend
git worktree add ../tdd-infra -b infra

# Verify creation
git worktree list
```

### 3. Create Setup Script
```bash
# scripts/setup-worktrees.sh
#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Creating git worktrees for parallel development..."

# Backend worktree
if [ ! -d "../tdd-backend" ]; then
    git worktree add ../tdd-backend -b backend 2>/dev/null || \
    git worktree add ../tdd-backend backend
fi

# Frontend worktree
if [ ! -d "../tdd-frontend" ]; then
    git worktree add ../tdd-frontend -b frontend 2>/dev/null || \
    git worktree add ../tdd-frontend frontend
fi

# Infrastructure worktree
if [ ! -d "../tdd-infra" ]; then
    git worktree add ../tdd-infra -b infra 2>/dev/null || \
    git worktree add ../tdd-infra infra
fi

echo "Worktrees created:"
git worktree list

echo ""
echo "Verifying beads sync across worktrees..."
for dir in ../tdd-backend ../tdd-frontend ../tdd-infra; do
    echo "  $dir: $(cd $dir && bd list --count 2>/dev/null || echo 'beads not initialized')"
done
```

### 4. Create Verification Script
```bash
# scripts/verify-environment.sh
#!/bin/bash
set -euo pipefail

echo "=== Environment Verification ==="

ERRORS=0

# Check git worktrees
echo -n "Git worktrees... "
if git worktree list | grep -q "tdd-backend" && \
   git worktree list | grep -q "tdd-frontend" && \
   git worktree list | grep -q "tdd-infra"; then
    echo "✓"
else
    echo "✗ Missing worktrees"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker
echo -n "Docker access... "
if docker info >/dev/null 2>&1; then
    echo "✓"
else
    echo "✗ Docker not accessible"
    ERRORS=$((ERRORS + 1))
fi

# Check beads
echo -n "Beads initialized... "
if [ -d ".beads" ]; then
    echo "✓"
else
    echo "✗ Run 'bd init'"
    ERRORS=$((ERRORS + 1))
fi

# Check Node.js
echo -n "Node.js... "
if command -v node >/dev/null 2>&1; then
    echo "✓ $(node --version)"
else
    echo "✗ Not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check Python
echo -n "Python 3.11+... "
if python3 --version 2>&1 | grep -qE "3\.(1[1-9]|[2-9][0-9])"; then
    echo "✓ $(python3 --version)"
else
    echo "✗ Need Python 3.11+"
    ERRORS=$((ERRORS + 1))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ Environment ready for parallel development"
    exit 0
else
    echo "❌ $ERRORS issues found - fix before proceeding"
    exit 1
fi
```

### 5. Create Editor Config
```ini
# .editorconfig
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.py]
indent_size = 4

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

### 6. Create Environment Template
```bash
# .env.example
# Copy to .env and fill in values

# Backend
DATABASE_URL=sqlite:///data/app.db
PROJECTS_ROOT=/projects
DEBUG=false

# Docker
DOCKER_HOST=unix:///var/run/docker.sock

# Claude API (for production - not needed for testing with mock)
# ANTHROPIC_API_KEY=sk-ant-...
```

## Beads Workflow

```bash
# Create your tracking issue
bd create --title="Environment: Setup worktrees and configs" --type=task --priority=0

# Mark as in progress
bd update <id> --status=in_progress

# When complete
bd close <id> --tag=environment-ready
bd sync
```

## Quality Gates

Before signaling completion:
```bash
# Run verification
./scripts/verify-environment.sh

# Verify all worktrees exist and are on correct branches
git worktree list

# Verify each worktree can access beads
for dir in ../tdd-backend ../tdd-frontend ../tdd-infra; do
    (cd "$dir" && bd list >/dev/null && echo "$dir: OK")
done
```

## Completion Criteria

- [ ] Directory structure created
- [ ] All three git worktrees created
- [ ] Each worktree on correct branch (backend, frontend, infra)
- [ ] Beads accessible from all worktrees
- [ ] Setup and verification scripts working
- [ ] .editorconfig and .env.example created
- [ ] Beads issue closed with `environment-ready` tag

## Coordination

After you complete, signal readiness:
```bash
bd comment <env-issue> "✅ Environment ready. Worktrees: tdd-backend, tdd-frontend, tdd-infra"
```

Domain agents can work in parallel with Contracts Agent finishing - they just need the worktrees ready.
