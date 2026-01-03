"""
Shared pytest fixtures for all backend tests.

This module provides common test fixtures that mirror the frozen contracts.
All fixtures are designed to be imported and used across test modules.
"""
import pytest
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
        container_id=None,
        github_url=None
    )


@pytest.fixture
def sample_container() -> Container:
    """A valid container for testing."""
    return Container(
        id="container-abc123",
        project_id="proj-001",
        status=ContainerStatus.CREATED,
        created_at=datetime.now(),
        image="claude-cli:latest"
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
