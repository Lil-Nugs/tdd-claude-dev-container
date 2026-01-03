#!/bin/bash
set -euo pipefail

echo "=== Environment Verification ==="

ERRORS=0

# Check git worktrees
echo -n "Git worktrees... "
if git worktree list | grep -q "tdd-backend" && \
   git worktree list | grep -q "tdd-frontend" && \
   git worktree list | grep -q "tdd-infra"; then
    echo "OK"
else
    echo "MISSING Missing worktrees"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker
echo -n "Docker access... "
if docker info >/dev/null 2>&1; then
    echo "OK"
else
    echo "FAIL Docker not accessible"
    ERRORS=$((ERRORS + 1))
fi

# Check beads
echo -n "Beads initialized... "
if [ -d ".beads" ]; then
    echo "OK"
else
    echo "FAIL Run 'bd init'"
    ERRORS=$((ERRORS + 1))
fi

# Check Node.js
echo -n "Node.js... "
if command -v node >/dev/null 2>&1; then
    echo "OK $(node --version)"
else
    echo "FAIL Not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check Python
echo -n "Python 3.11+... "
if python3 --version 2>&1 | grep -qE "3\.(1[1-9]|[2-9][0-9])"; then
    echo "OK $(python3 --version)"
else
    echo "FAIL Need Python 3.11+"
    ERRORS=$((ERRORS + 1))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "Environment ready for parallel development"
    exit 0
else
    echo "$ERRORS issues found - fix before proceeding"
    exit 1
fi
