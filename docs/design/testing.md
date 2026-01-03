# Testing Strategy

## Philosophy

**Test the pipes, not the water.**

Tests verify components connect correctly and data flows end-to-end. We do NOT test Claude's ability to write good code—that's manual testing.

### Principles

1. **Infrastructure over AI** - Test prompts reach Claude and responses reach UI, not what Claude says
2. **Failure recovery over happy paths** - Prioritize error handling, timeouts, reconnection
3. **CI-safe by default** - Real Claude tests run locally only
4. **Fast feedback** - Contract tests in seconds, integration in minutes

---

## Test Layers

### Layer 1: Contract Tests
**Purpose:** Validate API shapes and data contracts
**Speed:** Seconds
**CI:** Yes

```python
# backend/tests/contracts/test_project_contracts.py

def test_project_create_requires_name():
    with pytest.raises(ValidationError):
        ProjectCreate(name=None)

def test_project_response_includes_id():
    project = ProjectResponse(id="proj_123", name="my-project", ...)
    assert project.id is not None

def test_container_state_enum():
    assert ContainerState.RUNNING.value == "running"
    assert ContainerState.STOPPED.value == "stopped"

def test_websocket_message_schema():
    msg = WSMessage(type="output", payload={"data": "hello"})
    assert msg.type in ["output", "error", "status", "input"]
```

---

### Layer 2: Integration Tests
**Purpose:** Test component interactions with Docker (mock Claude)
**Speed:** Minutes
**CI:** Yes

#### Docker Lifecycle

```python
# backend/tests/integration/test_docker_manager.py

def test_container_lifecycle(docker_manager, tmp_path):
    container = docker_manager.create(project_path=tmp_path, image="claude-cli:test")

    docker_manager.start(container.id)
    assert docker_manager.get_status(container.id) == "running"

    docker_manager.stop(container.id)
    assert docker_manager.get_status(container.id) == "exited"

    docker_manager.remove(container.id)

def test_container_death_detected(docker_manager, tmp_path):
    container = docker_manager.create(project_path=tmp_path, image="claude-cli:test")
    docker_manager.start(container.id)
    docker_manager._client.containers.get(container.id).kill()

    assert docker_manager.get_status(container.id) in ["exited", "dead"]

def test_project_directory_mounted(docker_manager, tmp_path):
    (tmp_path / "test.txt").write_text("hello")
    container = docker_manager.create(project_path=tmp_path, image="claude-cli:test")
    docker_manager.start(container.id)

    result = docker_manager.exec(container.id, "cat /project/test.txt")
    assert "hello" in result.output
```

#### PTY Process Control

```python
# backend/tests/integration/test_cli_runner.py

def test_spawn_and_capture_output(cli_runner):
    process = cli_runner.spawn("echo 'hello world'")
    output = process.read_until_exit(timeout=5)
    assert "hello world" in output

def test_send_input_to_process(cli_runner):
    process = cli_runner.spawn("/bin/bash")
    process.send_input("echo 'from stdin'\n")
    output = process.read_until("from stdin", timeout=5)
    assert "from stdin" in output

def test_interrupt_process(cli_runner):
    process = cli_runner.spawn("sleep 300")
    time.sleep(0.5)
    process.interrupt()
    exit_code = process.wait(timeout=5)
    assert exit_code != 0

def test_mock_claude_io(cli_runner):
    process = cli_runner.spawn("/app/mock-claude.sh")
    process.send_input("Hello Claude\n")
    output = process.read_until("RECEIVED: Hello Claude", timeout=5)
    assert "RECEIVED: Hello Claude" in output
```

#### WebSocket Streaming

```python
# backend/tests/integration/test_websocket_stream.py

async def test_websocket_receives_output(ws_client):
    messages = []
    async for msg in ws_client.iter_messages(timeout=5):
        messages.append(msg)
        if len(messages) >= 1:
            break
    assert any(m["type"] == "output" for m in messages)

async def test_websocket_send_input(ws_client):
    await ws_client.send_json({"type": "input", "data": "test\n"})
    msg = await ws_client.receive_json(timeout=5)
    assert "test" in msg.get("data", "")

async def test_reconnect_receives_buffer(test_app, test_container):
    async with test_app.websocket_connect(f"/api/terminal/{test_container.id}") as ws:
        await ws.receive_json(timeout=5)
    # Reconnect
    async with test_app.websocket_connect(f"/api/terminal/{test_container.id}") as ws2:
        msg = await ws2.receive_json(timeout=5)
        assert msg is not None
```

#### Project Scaffolding

```python
# backend/tests/integration/test_project_scaffolding.py

def test_scaffold_creates_directory(scaffolder, tmp_path):
    scaffolder.create("my-project")
    assert (tmp_path / "my-project").is_dir()

def test_scaffold_initializes_git(scaffolder, tmp_path):
    scaffolder.create("my-project")
    assert (tmp_path / "my-project" / ".git").exists()

def test_scaffold_calls_gh_cli(scaffolder, mock_gh_cli):
    scaffolder.create("my-project")
    mock_gh_cli.assert_called_with(["repo", "create", "my-project", "--private", "--source=."])

def test_scaffold_rollback_on_failure(scaffolder, mock_gh_cli, tmp_path):
    mock_gh_cli.side_effect = GitHubError("Auth failed")
    with pytest.raises(ScaffoldError):
        scaffolder.create("my-project")
    assert not (tmp_path / "my-project").exists()
```

---

### Layer 3: Smoke Tests (Local Only)
**Purpose:** Verify real Claude CLI works
**Speed:** Slow (Claude response time)
**CI:** No (skip via marker)

```python
# backend/tests/smoke/test_real_claude.py

pytestmark = pytest.mark.local_only

def test_claude_responds(real_claude_runner):
    process = real_claude_runner.spawn("claude --dangerously-skip-permissions")
    process.read_until("Claude", timeout=30)
    process.send_input('Respond with exactly: SMOKE_TEST_OK\n')
    output = process.read_until("SMOKE_TEST_OK", timeout=60)
    assert "SMOKE_TEST_OK" in output

def test_claude_can_be_interrupted(real_claude_runner):
    process = real_claude_runner.spawn("claude --dangerously-skip-permissions")
    process.read_until("Claude", timeout=30)
    process.send_input('Write a 1000 word essay.\n')
    time.sleep(2)
    process.interrupt()
    # Should not hang
    process.wait(timeout=10)
```

---

### Layer 4: E2E Tests (Playwright)
**Purpose:** Full user workflows through UI
**Speed:** Slow
**CI:** Yes (with mock Claude)

```typescript
// frontend/tests/e2e/projects.spec.ts

test('can view project list', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /projects/i })).toBeVisible();
});

test('can create new project', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /new project/i }).click();
  await page.getByLabel('Project name').fill('test-project');
  await page.getByRole('button', { name: /create/i }).click();
  await expect(page.getByText('test-project')).toBeVisible();
});

test('terminal shows streamed output', async ({ page }) => {
  await page.goto('/projects/test-project/terminal');
  await expect(page.getByTestId('terminal')).toBeVisible();
  await expect(page.getByTestId('process-status')).toHaveText(/connected|ready/i);
});

test('can interrupt process', async ({ page }) => {
  await page.goto('/projects/test-project/terminal');
  await page.keyboard.type('sleep 300\n');
  await page.getByRole('button', { name: /interrupt/i }).click();
  await expect(page.getByTestId('process-status')).toHaveText('exited');
});

test('workflow shows progress', async ({ page }) => {
  await page.goto('/workflows');
  await page.getByLabel('Project').selectOption('test-project');
  await page.getByLabel('Workflow').selectOption('beads-work-cycle');
  await page.getByRole('button', { name: /start/i }).click();
  await expect(page.getByTestId('workflow-progress')).toBeVisible();
});
```

---

## Mock Claude

For CI-safe tests, use a mock that echoes I/O:

```bash
#!/bin/bash
# docker/claude-cli/mock-claude.sh

echo "Claude Code (mock mode)"
echo "Type your prompt..."

while IFS= read -r line; do
    echo "RECEIVED: $line"

    # Supported test behaviors:
    # STREAM:n  -> output n lines with delay
    # DELAY:ms  -> wait before responding
    # error     -> exit 1
    # hang      -> sleep forever (timeout tests)
    # exit      -> exit 0

    if [[ "$line" == *"error"* ]]; then
        echo "Error: Simulated error"
        exit 1
    fi
    if [[ "$line" == *"hang"* ]]; then
        sleep 300
    fi
    if [[ "$line" =~ exit|/exit|EXIT ]]; then
        echo "Goodbye!"
        exit 0
    fi
    echo "OK"
done
```

```dockerfile
# docker/claude-cli/Dockerfile.test
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y bash
COPY mock-claude.sh /usr/local/bin/claude
RUN chmod +x /usr/local/bin/claude
CMD ["/usr/local/bin/claude"]
```

---

## CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: cd backend && pip install -e ".[test]"
      - run: cd backend && pytest tests/contracts/ -v

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: cd backend && pip install -e ".[test]"
      - run: cd backend && pytest tests/integration/ -v

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci
      - run: cd frontend && npm run test:unit

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - uses: actions/setup-node@v4
      - run: cd backend && pip install -e ".[test]"
      - run: cd frontend && npm ci
      - run: cd frontend && npx playwright install --with-deps
      - run: cd backend && MOCK_CLAUDE=true python -m uvicorn app.main:app &
      - run: cd frontend && npm run build && npm run preview &
      - run: cd frontend && npm run test:e2e
```

---

## Test Markers

```python
# backend/conftest.py

def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: skip in CI")

def pytest_collection_modifyitems(config, items):
    if os.environ.get("CI"):
        skip_local = pytest.mark.skip(reason="Local-only test")
        for item in items:
            if "local_only" in item.keywords:
                item.add_marker(skip_local)
```

---

## Running Tests

```bash
# Quick validation (before commits)
cd backend && pytest tests/contracts/ -v

# Full local
cd backend && pytest
cd frontend && npm run test:unit
cd frontend && npm run test:e2e

# With real Claude (local only)
cd backend && pytest tests/smoke/ -v
```
