"""Database configuration using SQLModel."""

import os
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Create engine - use synchronous SQLite for simplicity
# For async, we'd use aiosqlite + async session
# Allow override for testing
database_url = os.environ.get("DATABASE_URL", settings.database_url)

# For SQLite, we need to handle the sqlite+aiosqlite:// prefix
if database_url.startswith("sqlite+aiosqlite"):
    database_url = database_url.replace("sqlite+aiosqlite", "sqlite")

# Use in-memory database for testing
if os.environ.get("TESTING") == "1":
    database_url = "sqlite:///:memory:"

engine = create_engine(
    database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False},  # Needed for SQLite
)


def create_db_and_tables() -> None:
    """Create database and tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    with Session(engine) as session:
        yield session
