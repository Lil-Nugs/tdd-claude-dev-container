"""Pytest configuration and fixtures."""

import os
import tempfile

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, delete, create_engine
from starlette.testclient import TestClient


# Create a temporary database file that persists across all tests
_temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_temp_db.close()
TEST_DATABASE_URL = f"sqlite:///{_temp_db.name}"

# Override the DATABASE_URL before importing app
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


# Import after setting env
from app.database import engine, get_session


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database once for all tests."""
    from app.models.project import Project  # noqa: F401

    SQLModel.metadata.create_all(engine)
    yield
    # Cleanup temp file
    try:
        os.unlink(_temp_db.name)
    except Exception:
        pass


@pytest.fixture(autouse=True)
def clean_database():
    """Clean database tables before each test."""
    from app.models.project import Project

    with Session(engine) as session:
        session.exec(delete(Project))
        session.commit()
    yield


@pytest.fixture
def app_with_test_db():
    """FastAPI app with test database."""
    from app.main import app
    yield app


@pytest.fixture
async def client(app_with_test_db):
    """Async test client for FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app_with_test_db),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def sync_client(app_with_test_db):
    """Sync test client for WebSocket tests."""
    return TestClient(app_with_test_db)


@pytest.fixture
def anyio_backend():
    """Use asyncio backend for anyio."""
    return "asyncio"
