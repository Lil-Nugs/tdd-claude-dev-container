#!/bin/bash
# docker/claude-cli/entrypoint.sh
# Entrypoint script for Claude CLI container

set -e

# Print environment info for debugging
echo "Claude CLI Container"
echo "===================="
echo "Node version: $(node --version 2>/dev/null || echo 'not installed')"
echo "Python version: $(python3 --version 2>/dev/null || echo 'not installed')"
echo "Git version: $(git --version 2>/dev/null || echo 'not installed')"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "===================="

# If mock-claude is available, make it executable
if [ -f /usr/local/bin/mock-claude ]; then
    echo "Mock Claude CLI available at /usr/local/bin/mock-claude"
fi

# Execute the command passed to the container
exec "$@"
