"""Sample project data for tests.

This module provides static test data for projects and workflows.
All data structures match the frozen contracts.
"""

SAMPLE_PROJECTS = [
    {
        "id": "proj-001",
        "name": "Web App",
        "path": "/projects/web-app",
        "created_at": "2024-01-15T10:00:00Z",
        "container_id": None,
        "github_url": None
    },
    {
        "id": "proj-002",
        "name": "API Service",
        "path": "/projects/api-service",
        "created_at": "2024-01-16T14:30:00Z",
        "container_id": "container-xyz789",
        "github_url": "https://github.com/user/api-service"
    }
]

SAMPLE_WORKFLOWS = [
    {
        "id": "wf-001",
        "name": "TDD Cycle",
        "description": "Test-driven development workflow",
        "steps": [
            {"name": "Run Tests", "command": "pytest", "review_after": False, "timeout_seconds": 300},
            {"name": "Implement", "command": "claude code", "review_after": True, "timeout_seconds": 300},
            {"name": "Refactor", "command": "claude refactor", "review_after": True, "timeout_seconds": 300}
        ],
        "loop_count": 3,
        "max_review_iterations": 5
    }
]

SAMPLE_CONTAINERS = [
    {
        "id": "container-xyz789",
        "project_id": "proj-002",
        "status": "running",
        "created_at": "2024-01-16T14:30:00Z",
        "image": "claude-cli:latest"
    }
]

SAMPLE_WORKFLOW_EXECUTIONS = [
    {
        "id": "exec-001",
        "workflow_id": "wf-001",
        "project_id": "proj-002",
        "status": "running",
        "current_step": 1,
        "current_loop": 0,
        "review_iteration": 2,
        "started_at": "2024-01-16T15:00:00Z",
        "completed_at": None,
        "error_message": None
    }
]
