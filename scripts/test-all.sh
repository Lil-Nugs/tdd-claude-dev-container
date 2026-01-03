#!/bin/bash
# scripts/test-all.sh
# Run all tests across the project

set -e

echo "=========================================="
echo "Running All Tests"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILED=0

# Function to run a test suite
run_test() {
    local name="$1"
    local cmd="$2"

    echo ""
    echo -e "${YELLOW}>>> Running: $name${NC}"
    echo "----------------------------------------"

    if eval "$cmd"; then
        echo -e "${GREEN}>>> PASSED: $name${NC}"
    else
        echo -e "${RED}>>> FAILED: $name${NC}"
        FAILED=$((FAILED + 1))
    fi
}

# Contract Tests
run_test "Contract Tests" "pytest backend/tests/contracts/ -v"

# Integration Tests
run_test "Integration Tests" "pytest backend/tests/integration/ -v"

# Frontend Unit Tests
run_test "Frontend Unit Tests" "cd frontend && npm run test:unit"

# E2E Tests (optional - requires services running)
if [ "$1" == "--with-e2e" ]; then
    run_test "E2E Tests" "cd frontend && npm run test:e2e"
fi

# Summary
echo ""
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}$FAILED test suite(s) failed${NC}"
    exit 1
fi
