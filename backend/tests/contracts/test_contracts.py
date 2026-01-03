"""
Contract validation tests - ensure types are serializable and valid.

These tests verify that all contract models:
1. Can be serialized to JSON
2. Can be deserialized from JSON
3. Maintain data integrity through round-trips
4. Enforce validation constraints
5. Have expected enum values for frontend compatibility
"""
import json
import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.app.models.contracts import (
    # Enums
    ContainerStatus,
    WorkflowStatus,
    TerminalMessageType,
    TerminalCommandType,
    # Project models
    CreateProject,
    Project,
    # Container models
    Container,
    # Terminal models
    TerminalMessage,
    TerminalCommand,
    TerminalResize,
    # Workflow models
    WorkflowStep,
    Workflow,
    WorkflowExecution,
    # Response wrappers
    ProjectList,
    ContainerList,
    WorkflowList,
    HealthCheck,
    ErrorResponse,
)


# =============================================================================
# ENUM TESTS - Verify enum values match frontend expectations
# =============================================================================

class TestContainerStatusEnum:
    """Tests for ContainerStatus enum."""

    def test_container_status_values(self):
        """ContainerStatus has expected values for frontend."""
        expected = {"created", "running", "exited", "error"}
        actual = {status.value for status in ContainerStatus}
        assert actual == expected

    def test_container_status_is_string_enum(self):
        """ContainerStatus values are strings for JSON serialization."""
        for status in ContainerStatus:
            assert isinstance(status.value, str)
            assert status.value == str(status.value)


class TestWorkflowStatusEnum:
    """Tests for WorkflowStatus enum."""

    def test_workflow_status_values(self):
        """WorkflowStatus has expected values for frontend."""
        expected = {"pending", "running", "paused", "completed", "failed", "cancelled"}
        actual = {status.value for status in WorkflowStatus}
        assert actual == expected


class TestTerminalEnums:
    """Tests for terminal-related enums."""

    def test_terminal_message_type_values(self):
        """TerminalMessageType has expected values."""
        expected = {"output", "input", "system", "error"}
        actual = {t.value for t in TerminalMessageType}
        assert actual == expected

    def test_terminal_command_type_values(self):
        """TerminalCommandType has expected values."""
        expected = {"input", "interrupt", "resize"}
        actual = {t.value for t in TerminalCommandType}
        assert actual == expected


# =============================================================================
# PROJECT MODEL TESTS
# =============================================================================

class TestCreateProject:
    """Tests for CreateProject model."""

    def test_create_project_minimal(self):
        """CreateProject with only required fields."""
        project = CreateProject(name="test", path="/test")
        assert project.name == "test"
        assert project.path == "/test"
        assert project.scaffold is True  # default
        assert project.github_private is True  # default

    def test_create_project_full(self):
        """CreateProject with all fields."""
        project = CreateProject(
            name="test",
            path="/test",
            scaffold=False,
            github_private=False
        )
        assert project.scaffold is False
        assert project.github_private is False

    def test_create_project_serialization(self):
        """CreateProject can round-trip to JSON."""
        project = CreateProject(name="test", path="/test")
        json_str = project.model_dump_json()
        restored = CreateProject.model_validate_json(json_str)
        assert restored == project

    def test_create_project_name_validation(self):
        """CreateProject validates name constraints."""
        # Empty name should fail
        with pytest.raises(ValidationError):
            CreateProject(name="", path="/test")

        # Name too long should fail
        with pytest.raises(ValidationError):
            CreateProject(name="x" * 101, path="/test")

    def test_create_project_path_validation(self):
        """CreateProject validates path constraints."""
        # Empty path should fail
        with pytest.raises(ValidationError):
            CreateProject(name="test", path="")


class TestProject:
    """Tests for Project model."""

    def test_project_serialization(self):
        """Project can round-trip to JSON."""
        now = datetime.utcnow()
        project = Project(
            id="550e8400-e29b-41d4-a716-446655440000",
            name="test",
            path="/test",
            created_at=now
        )
        json_str = project.model_dump_json()
        restored = Project.model_validate_json(json_str)
        assert restored.id == project.id
        assert restored.name == project.name
        assert restored.path == project.path

    def test_project_with_optional_fields(self):
        """Project with container_id and github_url."""
        project = Project(
            id="1",
            name="test",
            path="/test",
            created_at=datetime.utcnow(),
            container_id="abc123",
            github_url="https://github.com/user/test"
        )
        json_str = project.model_dump_json()
        restored = Project.model_validate_json(json_str)
        assert restored.container_id == "abc123"
        assert restored.github_url == "https://github.com/user/test"

    def test_project_optional_fields_null(self):
        """Project optional fields can be null."""
        project = Project(
            id="1",
            name="test",
            path="/test",
            created_at=datetime.utcnow(),
            container_id=None,
            github_url=None
        )
        assert project.container_id is None
        assert project.github_url is None


# =============================================================================
# CONTAINER MODEL TESTS
# =============================================================================

class TestContainer:
    """Tests for Container model."""

    def test_container_serialization(self):
        """Container can round-trip to JSON."""
        container = Container(
            id="abc123",
            project_id="proj-1",
            status=ContainerStatus.RUNNING,
            created_at=datetime.utcnow(),
            image="claude-cli:latest"
        )
        json_str = container.model_dump_json()
        restored = Container.model_validate_json(json_str)
        assert restored.id == container.id
        assert restored.project_id == container.project_id
        assert restored.status == ContainerStatus.RUNNING

    def test_container_status_serializes_as_string(self):
        """Container status serializes as string value."""
        container = Container(
            id="abc123",
            project_id="proj-1",
            status=ContainerStatus.RUNNING,
            created_at=datetime.utcnow()
        )
        data = json.loads(container.model_dump_json())
        assert data["status"] == "running"

    def test_container_default_image(self):
        """Container has default image."""
        container = Container(
            id="abc123",
            project_id="proj-1",
            status=ContainerStatus.CREATED,
            created_at=datetime.utcnow()
        )
        assert container.image == "claude-cli:latest"


# =============================================================================
# TERMINAL MODEL TESTS
# =============================================================================

class TestTerminalMessage:
    """Tests for TerminalMessage model."""

    def test_terminal_message_serialization(self):
        """TerminalMessage can round-trip to JSON."""
        msg = TerminalMessage(
            type=TerminalMessageType.OUTPUT,
            data="Hello, world!\n"
        )
        json_str = msg.model_dump_json()
        restored = TerminalMessage.model_validate_json(json_str)
        assert restored.type == TerminalMessageType.OUTPUT
        assert restored.data == "Hello, world!\n"

    def test_terminal_message_type_serializes_as_string(self):
        """Terminal message type serializes as string."""
        msg = TerminalMessage(
            type=TerminalMessageType.OUTPUT,
            data="test"
        )
        data = json.loads(msg.model_dump_json())
        assert data["type"] == "output"

    def test_terminal_message_has_timestamp(self):
        """TerminalMessage gets default timestamp."""
        msg = TerminalMessage(
            type=TerminalMessageType.OUTPUT,
            data="test"
        )
        assert msg.timestamp is not None
        assert isinstance(msg.timestamp, datetime)


class TestTerminalCommand:
    """Tests for TerminalCommand model."""

    def test_terminal_command_input(self):
        """TerminalCommand for input."""
        cmd = TerminalCommand(
            type=TerminalCommandType.INPUT,
            data="bd list\n"
        )
        json_str = cmd.model_dump_json()
        restored = TerminalCommand.model_validate_json(json_str)
        assert restored.type == TerminalCommandType.INPUT
        assert restored.data == "bd list\n"

    def test_terminal_command_interrupt(self):
        """TerminalCommand for interrupt (no data)."""
        cmd = TerminalCommand(type=TerminalCommandType.INTERRUPT)
        assert cmd.data is None
        json_str = cmd.model_dump_json()
        restored = TerminalCommand.model_validate_json(json_str)
        assert restored.type == TerminalCommandType.INTERRUPT


class TestTerminalResize:
    """Tests for TerminalResize model."""

    def test_terminal_resize_serialization(self):
        """TerminalResize can round-trip to JSON."""
        resize = TerminalResize(cols=80, rows=24)
        json_str = resize.model_dump_json()
        restored = TerminalResize.model_validate_json(json_str)
        assert restored.cols == 80
        assert restored.rows == 24

    def test_terminal_resize_validation(self):
        """TerminalResize validates dimensions."""
        # Valid dimensions
        resize = TerminalResize(cols=120, rows=40)
        assert resize.cols == 120

        # Invalid dimensions
        with pytest.raises(ValidationError):
            TerminalResize(cols=0, rows=24)

        with pytest.raises(ValidationError):
            TerminalResize(cols=80, rows=0)

        with pytest.raises(ValidationError):
            TerminalResize(cols=501, rows=24)

        with pytest.raises(ValidationError):
            TerminalResize(cols=80, rows=201)


# =============================================================================
# WORKFLOW MODEL TESTS
# =============================================================================

class TestWorkflowStep:
    """Tests for WorkflowStep model."""

    def test_workflow_step_minimal(self):
        """WorkflowStep with only required fields."""
        step = WorkflowStep(name="Pull ready", command="bd ready")
        assert step.name == "Pull ready"
        assert step.command == "bd ready"
        assert step.review_after is False  # default
        assert step.timeout_seconds == 300  # default

    def test_workflow_step_serialization(self):
        """WorkflowStep can round-trip to JSON."""
        step = WorkflowStep(
            name="Implement",
            command="claude code",
            review_after=True,
            timeout_seconds=600
        )
        json_str = step.model_dump_json()
        restored = WorkflowStep.model_validate_json(json_str)
        assert restored == step

    def test_workflow_step_timeout_validation(self):
        """WorkflowStep validates timeout bounds."""
        # Valid timeout
        step = WorkflowStep(name="test", command="test", timeout_seconds=60)
        assert step.timeout_seconds == 60

        # Invalid timeouts
        with pytest.raises(ValidationError):
            WorkflowStep(name="test", command="test", timeout_seconds=0)

        with pytest.raises(ValidationError):
            WorkflowStep(name="test", command="test", timeout_seconds=3601)


class TestWorkflow:
    """Tests for Workflow model."""

    def test_workflow_serialization(self):
        """Workflow can round-trip to JSON."""
        workflow = Workflow(
            id="beads-work-cycle",
            name="Beads Work Cycle",
            description="Pull ready issue, implement, review, close",
            steps=[
                WorkflowStep(name="Pull ready", command="bd ready"),
                WorkflowStep(name="Implement", command="claude code", review_after=True)
            ],
            loop_count=3,
            max_review_iterations=5
        )
        json_str = workflow.model_dump_json()
        restored = Workflow.model_validate_json(json_str)
        assert restored.id == workflow.id
        assert len(restored.steps) == 2
        assert restored.loop_count == 3

    def test_workflow_requires_steps(self):
        """Workflow must have at least one step."""
        with pytest.raises(ValidationError):
            Workflow(id="test", name="test", steps=[])

    def test_workflow_defaults(self):
        """Workflow has sensible defaults."""
        workflow = Workflow(
            id="test",
            name="test",
            steps=[WorkflowStep(name="step", command="cmd")]
        )
        assert workflow.description == ""
        assert workflow.loop_count == 1
        assert workflow.max_review_iterations == 5


class TestWorkflowExecution:
    """Tests for WorkflowExecution model."""

    def test_workflow_execution_serialization(self):
        """WorkflowExecution can round-trip to JSON."""
        execution = WorkflowExecution(
            id="exec-001",
            workflow_id="beads-work-cycle",
            project_id="proj-1",
            status=WorkflowStatus.RUNNING,
            current_step=1,
            current_loop=0,
            review_iteration=2,
            started_at=datetime.utcnow()
        )
        json_str = execution.model_dump_json()
        restored = WorkflowExecution.model_validate_json(json_str)
        assert restored.id == execution.id
        assert restored.status == WorkflowStatus.RUNNING
        assert restored.current_step == 1

    def test_workflow_execution_completed(self):
        """WorkflowExecution with completion data."""
        now = datetime.utcnow()
        execution = WorkflowExecution(
            id="exec-001",
            workflow_id="beads-work-cycle",
            project_id="proj-1",
            status=WorkflowStatus.COMPLETED,
            current_step=2,
            current_loop=3,
            review_iteration=0,
            started_at=now,
            completed_at=now
        )
        assert execution.completed_at is not None
        assert execution.error_message is None

    def test_workflow_execution_failed(self):
        """WorkflowExecution with failure data."""
        execution = WorkflowExecution(
            id="exec-001",
            workflow_id="beads-work-cycle",
            project_id="proj-1",
            status=WorkflowStatus.FAILED,
            started_at=datetime.utcnow(),
            error_message="Container exited unexpectedly"
        )
        assert execution.status == WorkflowStatus.FAILED
        assert execution.error_message == "Container exited unexpectedly"


# =============================================================================
# RESPONSE WRAPPER TESTS
# =============================================================================

class TestProjectList:
    """Tests for ProjectList response model."""

    def test_project_list_serialization(self):
        """ProjectList can round-trip to JSON."""
        projects = [
            Project(
                id="1",
                name="project1",
                path="/proj1",
                created_at=datetime.utcnow()
            ),
            Project(
                id="2",
                name="project2",
                path="/proj2",
                created_at=datetime.utcnow()
            )
        ]
        project_list = ProjectList(projects=projects, total=2)
        json_str = project_list.model_dump_json()
        restored = ProjectList.model_validate_json(json_str)
        assert len(restored.projects) == 2
        assert restored.total == 2

    def test_project_list_empty(self):
        """ProjectList can be empty."""
        project_list = ProjectList(projects=[], total=0)
        assert project_list.projects == []
        assert project_list.total == 0


class TestContainerList:
    """Tests for ContainerList response model."""

    def test_container_list_serialization(self):
        """ContainerList can round-trip to JSON."""
        containers = [
            Container(
                id="c1",
                project_id="p1",
                status=ContainerStatus.RUNNING,
                created_at=datetime.utcnow()
            )
        ]
        container_list = ContainerList(containers=containers, total=1)
        json_str = container_list.model_dump_json()
        restored = ContainerList.model_validate_json(json_str)
        assert len(restored.containers) == 1


class TestWorkflowList:
    """Tests for WorkflowList response model."""

    def test_workflow_list_serialization(self):
        """WorkflowList can round-trip to JSON."""
        workflows = [
            Workflow(
                id="wf1",
                name="Workflow 1",
                steps=[WorkflowStep(name="step", command="cmd")]
            )
        ]
        workflow_list = WorkflowList(workflows=workflows, total=1)
        json_str = workflow_list.model_dump_json()
        restored = WorkflowList.model_validate_json(json_str)
        assert len(restored.workflows) == 1


class TestHealthCheck:
    """Tests for HealthCheck response model."""

    def test_health_check_serialization(self):
        """HealthCheck can round-trip to JSON."""
        health = HealthCheck(
            status="healthy",
            docker_available=True,
            version="1.0.0"
        )
        json_str = health.model_dump_json()
        restored = HealthCheck.model_validate_json(json_str)
        assert restored.status == "healthy"
        assert restored.docker_available is True
        assert restored.version == "1.0.0"

    def test_health_check_status_validation(self):
        """HealthCheck validates status literal."""
        # Valid statuses
        for status in ["healthy", "degraded", "unhealthy"]:
            health = HealthCheck(status=status, docker_available=True, version="1.0.0")
            assert health.status == status

        # Invalid status
        with pytest.raises(ValidationError):
            HealthCheck(status="invalid", docker_available=True, version="1.0.0")


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_error_response_serialization(self):
        """ErrorResponse can round-trip to JSON."""
        error = ErrorResponse(
            error="NOT_FOUND",
            message="Project not found",
            details={"project_id": "abc123"}
        )
        json_str = error.model_dump_json()
        restored = ErrorResponse.model_validate_json(json_str)
        assert restored.error == "NOT_FOUND"
        assert restored.message == "Project not found"
        assert restored.details == {"project_id": "abc123"}

    def test_error_response_without_details(self):
        """ErrorResponse works without details."""
        error = ErrorResponse(
            error="INTERNAL_ERROR",
            message="Something went wrong"
        )
        assert error.details is None


# =============================================================================
# CROSS-CUTTING TESTS
# =============================================================================

class TestJsonSerializability:
    """Tests ensuring all models produce valid JSON."""

    def test_all_models_produce_valid_json(self):
        """All contract models produce parseable JSON."""
        now = datetime.utcnow()

        models = [
            CreateProject(name="test", path="/test"),
            Project(id="1", name="test", path="/test", created_at=now),
            Container(id="c1", project_id="p1", status=ContainerStatus.RUNNING, created_at=now),
            TerminalMessage(type=TerminalMessageType.OUTPUT, data="test"),
            TerminalCommand(type=TerminalCommandType.INPUT, data="test"),
            TerminalResize(cols=80, rows=24),
            WorkflowStep(name="step", command="cmd"),
            Workflow(id="wf", name="wf", steps=[WorkflowStep(name="s", command="c")]),
            WorkflowExecution(
                id="e1", workflow_id="wf", project_id="p1",
                status=WorkflowStatus.RUNNING, started_at=now
            ),
            ProjectList(projects=[], total=0),
            ContainerList(containers=[], total=0),
            WorkflowList(workflows=[], total=0),
            HealthCheck(status="healthy", docker_available=True, version="1.0.0"),
            ErrorResponse(error="TEST", message="test"),
        ]

        for model in models:
            json_str = model.model_dump_json()
            # Should not raise
            parsed = json.loads(json_str)
            assert isinstance(parsed, dict)


class TestDatetimeSerialization:
    """Tests ensuring datetime fields serialize correctly for frontend."""

    def test_datetime_serializes_as_iso_string(self):
        """Datetime fields serialize as ISO 8601 strings."""
        now = datetime(2026, 1, 3, 12, 0, 0)
        project = Project(id="1", name="test", path="/test", created_at=now)
        data = json.loads(project.model_dump_json())

        # Should be a string, not a timestamp
        assert isinstance(data["created_at"], str)
        # Should be parseable as ISO 8601
        assert "2026" in data["created_at"]
