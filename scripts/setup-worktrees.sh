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
