"""Project model and schemas."""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class ProjectBase(SQLModel):
    """Base project schema."""

    name: str = Field(index=True)
    description: Optional[str] = None
    github_url: Optional[str] = None
    local_path: Optional[str] = None
    container_id: Optional[str] = None


class Project(ProjectBase, table=True):
    """Project database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(SQLModel):
    """Schema for updating a project."""

    name: Optional[str] = None
    description: Optional[str] = None
    github_url: Optional[str] = None
    local_path: Optional[str] = None
    container_id: Optional[str] = None


class ProjectRead(ProjectBase):
    """Schema for reading a project."""

    id: int
    created_at: datetime
    updated_at: datetime
