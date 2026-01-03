"""
Shared API contracts - FROZEN after Phase 0.
All agents must implement against these exactly.

This module defines the canonical data structures used across the entire system.
Both backend implementation and frontend TypeScript types must match these definitions.

Generated: 2026-01-03
Status: FROZEN - Do not modify without full team coordination.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Literal


# =============================================================================
# ENUMS - Define allowed values for type-safe fields
# =============================================================================

class ContainerStatus(str, Enum):
    """Status of a Docker container running Claude CLI."""
    CREATED = "created"
    RUNNING = "running"
    EXITED = "exited"
    ERROR = "error"


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TerminalMessageType(str, Enum):
    """Type of terminal message for WebSocket communication."""
    OUTPUT = "output"       # CLI stdout/stderr output
    INPUT = "input"         # User input echo
    SYSTEM = "system"       # System messages (connect, disconnect, etc.)
    ERROR = "error"         # Error messages


class TerminalCommandType(str, Enum):
    """Type of command that can be sent to the terminal."""
    INPUT = "input"         # Send text input to CLI
    INTERRUPT = "interrupt"  # Send SIGINT (Ctrl+C)
    RESIZE = "resize"       # Resize terminal dimensions


# =============================================================================
# PROJECT MODELS
# =============================================================================

class ProjectBase(BaseModel):
    """Base fields shared by Project models."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable project name"
    )
    path: str = Field(
        ...,
        min_length=1,
        description="Filesystem path to project directory"
    )


class CreateProject(ProjectBase):
    """Request model for creating a new project."""
    scaffold: bool = Field(
        default=True,
        description="Whether to scaffold the project with git, GitHub, and beads"
    )
    github_private: bool = Field(
        default=True,
        description="Whether to create a private GitHub repository"
    )


class Project(ProjectBase):
    """Full project model with all fields."""
    id: str = Field(
        ...,
        description="Unique project identifier (UUID)"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when project was created"
    )
    container_id: str | None = Field(
        default=None,
        description="ID of associated Docker container, if any"
    )
    github_url: str | None = Field(
        default=None,
        description="URL of GitHub repository, if created"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "my-project",
                "path": "/home/user/projects/my-project",
                "created_at": "2026-01-03T12:00:00Z",
                "container_id": "abc123def456",
                "github_url": "https://github.com/user/my-project"
            }
        }
    }


# =============================================================================
# CONTAINER MODELS
# =============================================================================

class Container(BaseModel):
    """Docker container running Claude CLI for a project."""
    id: str = Field(
        ...,
        description="Docker container ID"
    )
    project_id: str = Field(
        ...,
        description="ID of the project this container serves"
    )
    status: ContainerStatus = Field(
        ...,
        description="Current container status"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when container was created"
    )
    image: str = Field(
        default="claude-cli:latest",
        description="Docker image used for the container"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "abc123def456",
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "running",
                "created_at": "2026-01-03T12:00:00Z",
                "image": "claude-cli:latest"
            }
        }
    }


# =============================================================================
# TERMINAL/WEBSOCKET MODELS
# =============================================================================

class TerminalMessage(BaseModel):
    """Message sent from server to client via WebSocket."""
    type: TerminalMessageType = Field(
        ...,
        description="Type of terminal message"
    )
    data: str = Field(
        ...,
        description="Message content (output text, system message, etc.)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the message was generated"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "output",
                "data": "Hello, world!\n",
                "timestamp": "2026-01-03T12:00:00Z"
            }
        }
    }


class TerminalCommand(BaseModel):
    """Command sent from client to server via WebSocket."""
    type: TerminalCommandType = Field(
        ...,
        description="Type of command"
    )
    data: str | None = Field(
        default=None,
        description="Command payload (input text, resize dimensions, etc.)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "input",
                "data": "bd list\n"
            }
        }
    }


class TerminalResize(BaseModel):
    """Terminal resize dimensions."""
    cols: int = Field(
        ...,
        ge=1,
        le=500,
        description="Number of columns"
    )
    rows: int = Field(
        ...,
        ge=1,
        le=200,
        description="Number of rows"
    )


# =============================================================================
# WORKFLOW MODELS
# =============================================================================

class WorkflowStep(BaseModel):
    """A single step in a workflow."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable step name"
    )
    command: str = Field(
        ...,
        min_length=1,
        description="Command to execute (may contain {placeholders})"
    )
    review_after: bool = Field(
        default=False,
        description="Whether to trigger self-review after this step"
    )
    timeout_seconds: int = Field(
        default=300,
        ge=1,
        le=3600,
        description="Maximum time for step execution in seconds"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Pull ready issue",
                "command": "bd ready",
                "review_after": False,
                "timeout_seconds": 60
            }
        }
    }


class Workflow(BaseModel):
    """A workflow template defining a sequence of steps."""
    id: str = Field(
        ...,
        description="Unique workflow identifier"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable workflow name"
    )
    description: str = Field(
        default="",
        max_length=500,
        description="Workflow description"
    )
    steps: list[WorkflowStep] = Field(
        ...,
        min_length=1,
        description="Ordered list of steps to execute"
    )
    loop_count: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Number of times to repeat the workflow"
    )
    max_review_iterations: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum self-review iterations before proceeding"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "beads-work-cycle",
                "name": "Beads Work Cycle",
                "description": "Pull ready issue, implement, review, close, repeat",
                "steps": [
                    {"name": "Pull ready", "command": "bd ready", "review_after": False},
                    {"name": "Implement", "command": "claude code", "review_after": True}
                ],
                "loop_count": 3,
                "max_review_iterations": 5
            }
        }
    }


class WorkflowExecution(BaseModel):
    """A running or completed workflow execution."""
    id: str = Field(
        ...,
        description="Unique execution identifier"
    )
    workflow_id: str = Field(
        ...,
        description="ID of the workflow being executed"
    )
    project_id: str = Field(
        ...,
        description="ID of the project running this workflow"
    )
    status: WorkflowStatus = Field(
        ...,
        description="Current execution status"
    )
    current_step: int = Field(
        default=0,
        ge=0,
        description="Index of currently executing step (0-based)"
    )
    current_loop: int = Field(
        default=0,
        ge=0,
        description="Current loop iteration (0-based)"
    )
    review_iteration: int = Field(
        default=0,
        ge=0,
        description="Current review iteration for the current step"
    )
    started_at: datetime = Field(
        ...,
        description="When execution started"
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When execution completed, if finished"
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if execution failed"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "exec-001",
                "workflow_id": "beads-work-cycle",
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "running",
                "current_step": 1,
                "current_loop": 0,
                "review_iteration": 2,
                "started_at": "2026-01-03T12:00:00Z",
                "completed_at": None,
                "error_message": None
            }
        }
    }


# =============================================================================
# API RESPONSE WRAPPERS
# =============================================================================

class ProjectList(BaseModel):
    """Response model for listing projects."""
    projects: list[Project] = Field(
        default_factory=list,
        description="List of projects"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of projects"
    )


class ContainerList(BaseModel):
    """Response model for listing containers."""
    containers: list[Container] = Field(
        default_factory=list,
        description="List of containers"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of containers"
    )


class WorkflowList(BaseModel):
    """Response model for listing workflow templates."""
    workflows: list[Workflow] = Field(
        default_factory=list,
        description="List of workflow templates"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of workflows"
    )


class HealthCheck(BaseModel):
    """Health check response."""
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ...,
        description="Overall service health status"
    )
    docker_available: bool = Field(
        ...,
        description="Whether Docker daemon is accessible"
    )
    version: str = Field(
        ...,
        description="API version"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(
        ...,
        description="Error type/code"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    details: dict | None = Field(
        default=None,
        description="Additional error details"
    )
