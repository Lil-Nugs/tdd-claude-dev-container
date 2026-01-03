# Fixture Agent Instructions

You are the **Fixture Agent** responsible for creating shared test infrastructure before parallel implementation begins.

## Your Role

You run in **Phase 0** after the Contracts Agent completes. You create test fixtures, mocks, and shared test utilities that all domain agents will use.

## Your Domain

You may **ONLY** modify files in:
```
backend/tests/conftest.py
backend/tests/fixtures/
frontend/tests/fixtures/
tests/shared/
docker/claude-cli/mock-claude.sh
```

**DO NOT** implement actual features - only test infrastructure.

## Your Responsibilities

### 1. Create Backend Test Fixtures

```python
# backend/tests/conftest.py
"""
Shared pytest fixtures for all backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

# Import contracts for type-safe fixtures
from app.models.contracts import Project, Container, ContainerStatus


@pytest.fixture
def sample_project() -> Project:
    """A valid project for testing."""
    return Project(
        id="proj-001",
        name="Test Project",
        path="/projects/test-project",
        created_at=datetime.now(),
        container_id=None
    )


@pytest.fixture
def sample_container() -> Container:
    """A valid container for testing."""
    return Container(
        id="container-abc123",
        project_id="proj-001",
        status=ContainerStatus.CREATED
    )


@pytest.fixture
def mock_docker_client():
    """Mock Docker client for unit tests."""
    mock = MagicMock()
    mock.containers.run = MagicMock(return_value=MagicMock(id="mock-container-id"))
    mock.containers.get = MagicMock(return_value=MagicMock(
        id="mock-container-id",
        status="running"
    ))
    mock.containers.list = MagicMock(return_value=[])
    return mock


@pytest.fixture
def mock_pty_process():
    """Mock PTY process for CLI runner tests."""
    mock = MagicMock()
    mock.pid = 12345
    mock.fd = 3
    mock.read = MagicMock(return_value=b"Mock output\n")
    mock.write = MagicMock()
    mock.terminate = MagicMock()
    return mock


@pytest.fixture
async def async_mock_websocket():
    """Mock WebSocket connection for terminal tests."""
    mock = AsyncMock()
    mock.accept = AsyncMock()
    mock.send_json = AsyncMock()
    mock.receive_json = AsyncMock(return_value={"type": "input", "data": "test"})
    mock.close = AsyncMock()
    return mock
```

### 2. Create Backend Fixture Data

```python
# backend/tests/fixtures/projects.py
"""Sample project data for tests."""

SAMPLE_PROJECTS = [
    {
        "id": "proj-001",
        "name": "Web App",
        "path": "/projects/web-app",
        "created_at": "2024-01-15T10:00:00Z",
        "container_id": None
    },
    {
        "id": "proj-002",
        "name": "API Service",
        "path": "/projects/api-service",
        "created_at": "2024-01-16T14:30:00Z",
        "container_id": "container-xyz789"
    }
]

SAMPLE_WORKFLOWS = [
    {
        "id": "wf-001",
        "name": "TDD Cycle",
        "steps": [
            {"name": "Run Tests", "command": "pytest", "review_after": False},
            {"name": "Implement", "command": "claude code", "review_after": True},
            {"name": "Refactor", "command": "claude refactor", "review_after": True}
        ],
        "loop_count": 3
    }
]
```

### 3. Create Mock Claude CLI

```bash
#!/bin/bash
# docker/claude-cli/mock-claude.sh
# Mock Claude CLI for testing without API calls

set -euo pipefail

VERSION="mock-1.0.0"

# Parse arguments
case "${1:-}" in
    --version|-v)
        echo "Claude CLI $VERSION (mock)"
        exit 0
        ;;
    --help|-h)
        echo "Mock Claude CLI for testing"
        echo ""
        echo "Commands:"
        echo "  STREAM      - Output text with delay (simulates streaming)"
        echo "  DELAY:N     - Wait N seconds"
        echo "  ERROR       - Exit with error code 1"
        echo "  HANG        - Never exit (for interrupt testing)"
        echo "  EXIT        - Exit cleanly"
        echo "  ECHO:text   - Echo back the text"
        echo ""
        exit 0
        ;;
esac

echo "Mock Claude CLI $VERSION"
echo "Ready for input..."

while IFS= read -r line || [[ -n "$line" ]]; do
    case "$line" in
        STREAM)
            for i in {1..5}; do
                echo "Streaming response line $i..."
                sleep 0.1
            done
            echo "Stream complete."
            ;;
        DELAY:*)
            seconds="${line#DELAY:}"
            echo "Waiting $seconds seconds..."
            sleep "$seconds"
            echo "Done waiting."
            ;;
        ERROR)
            echo "Error: Simulated failure" >&2
            exit 1
            ;;
        ERROR:*)
            message="${line#ERROR:}"
            echo "Error: $message" >&2
            exit 1
            ;;
        HANG)
            echo "Hanging forever (send SIGINT to stop)..."
            trap 'echo "Interrupted!"; exit 130' INT TERM
            while true; do sleep 1; done
            ;;
        EXIT|exit|quit)
            echo "Exiting normally."
            exit 0
            ;;
        EXIT:*)
            code="${line#EXIT:}"
            echo "Exiting with code $code"
            exit "$code"
            ;;
        ECHO:*)
            text="${line#ECHO:}"
            echo "$text"
            ;;
        JSON:*)
            json="${line#JSON:}"
            echo "$json"
            ;;
        "")
            # Ignore empty lines
            ;;
        *)
            # Default: echo back with prefix
            echo "Claude: $line"
            ;;
    esac
done
```

### 4. Create Frontend Test Fixtures

```typescript
// frontend/tests/fixtures/api-mocks.ts
/**
 * Mock API responses for frontend tests.
 */
import type { Project, Container, Workflow } from '$lib/types/api';

export const mockProjects: Project[] = [
  {
    id: 'proj-001',
    name: 'Web App',
    path: '/projects/web-app',
    created_at: '2024-01-15T10:00:00Z',
    container_id: undefined
  },
  {
    id: 'proj-002',
    name: 'API Service',
    path: '/projects/api-service',
    created_at: '2024-01-16T14:30:00Z',
    container_id: 'container-xyz789'
  }
];

export const mockContainers: Container[] = [
  {
    id: 'container-xyz789',
    project_id: 'proj-002',
    status: 'running'
  }
];

export const mockWorkflows: Workflow[] = [
  {
    id: 'wf-001',
    name: 'TDD Cycle',
    steps: [
      { name: 'Run Tests', command: 'pytest', review_after: false },
      { name: 'Implement', command: 'claude code', review_after: true },
      { name: 'Refactor', command: 'claude refactor', review_after: true }
    ],
    loop_count: 3
  }
];

/**
 * Create a mock fetch that returns predefined responses.
 */
export function createMockFetch(responses: Record<string, unknown>) {
  return async (url: string, options?: RequestInit): Promise<Response> => {
    const path = url.replace(/^.*\/api/, '/api');

    if (path in responses) {
      return new Response(JSON.stringify(responses[path]), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    });
  };
}
```

```typescript
// frontend/tests/fixtures/websocket-mock.ts
/**
 * Mock WebSocket for terminal testing.
 */

export class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;

  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((error: Error) => void) | null = null;

  private messageQueue: string[] = [];

  constructor(url: string) {
    this.url = url;
    // Simulate connection delay
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.();
    }, 10);
  }

  send(data: string): void {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error('WebSocket is not open');
    }
    // Echo back for testing
    const parsed = JSON.parse(data);
    if (parsed.type === 'input') {
      this.simulateMessage({
        type: 'output',
        data: `Echo: ${parsed.data}`
      });
    }
  }

  close(): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.();
  }

  /**
   * Simulate receiving a message from server.
   */
  simulateMessage(message: object): void {
    setTimeout(() => {
      this.onmessage?.({ data: JSON.stringify(message) });
    }, 0);
  }

  /**
   * Simulate a stream of output.
   */
  simulateStream(lines: string[], delayMs = 50): void {
    lines.forEach((line, i) => {
      setTimeout(() => {
        this.simulateMessage({ type: 'output', data: line + '\n' });
      }, delayMs * i);
    });
  }
}
```

## Beads Workflow

```bash
# Wait for contracts to be ready first
bd list --tag=contracts-frozen

# Create your tracking issue
bd create --title="Fixtures: Create shared test infrastructure" --type=task --priority=0

# Mark as in progress
bd update <id> --status=in_progress

# When complete
bd close <id> --tag=fixtures-ready
bd sync
```

## Quality Gates

Before signaling completion:
```bash
# Verify Python fixtures are importable
python -c "from backend.tests.conftest import *; print('OK')"
python -c "from backend.tests.fixtures.projects import *; print('OK')"

# Verify mock-claude works
chmod +x docker/claude-cli/mock-claude.sh
echo "STREAM" | docker/claude-cli/mock-claude.sh
echo "EXIT" | docker/claude-cli/mock-claude.sh

# Verify TypeScript fixtures compile
cd frontend && npx tsc --noEmit tests/fixtures/*.ts
```

## Completion Criteria

- [ ] Backend conftest.py with common fixtures
- [ ] Backend fixture data files
- [ ] Mock Docker client fixture
- [ ] Mock PTY process fixture
- [ ] mock-claude.sh tested and working
- [ ] Frontend API mock utilities
- [ ] Frontend WebSocket mock
- [ ] All fixtures importable/compilable
- [ ] Beads issue closed with `fixtures-ready` tag

## Coordination

After you complete, signal readiness:
```bash
bd comment <fixtures-issue> "✅ Test fixtures ready. Domain agents can use shared mocks."
```
