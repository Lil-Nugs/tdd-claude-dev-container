"""Integration tests for Docker manager."""

import pytest

from app.services.docker_manager import DockerManager


@pytest.fixture
def docker_manager():
    """Create a DockerManager instance."""
    return DockerManager()


class TestDockerManagerConnection:
    """Tests for Docker connection functionality."""

    def test_docker_manager_can_be_instantiated(self, docker_manager):
        """DockerManager should instantiate without error."""
        assert docker_manager is not None

    def test_docker_manager_has_client(self, docker_manager):
        """DockerManager should have a Docker client."""
        assert docker_manager.client is not None

    def test_docker_manager_can_ping(self, docker_manager):
        """DockerManager should be able to ping Docker daemon."""
        result = docker_manager.ping()
        assert result is True


class TestDockerManagerContainers:
    """Tests for container management functionality."""

    def test_list_containers_returns_list(self, docker_manager):
        """list_containers should return a list."""
        containers = docker_manager.list_containers()
        assert isinstance(containers, list)

    def test_list_containers_includes_all_when_requested(self, docker_manager):
        """list_containers with all=True should include stopped containers."""
        containers = docker_manager.list_containers(all_containers=True)
        assert isinstance(containers, list)


class TestDockerManagerImages:
    """Tests for image management functionality."""

    def test_list_images_returns_list(self, docker_manager):
        """list_images should return a list."""
        images = docker_manager.list_images()
        assert isinstance(images, list)


class TestContainerLifecycle:
    """Tests for container lifecycle management."""

    @pytest.fixture
    def test_container_name(self):
        """Unique container name for tests."""
        return "test-backend-container"

    def test_create_container_returns_container_id(self, docker_manager, test_container_name):
        """Creating a container should return container ID."""
        try:
            container_id = docker_manager.create_container(
                image="alpine:latest",
                name=test_container_name,
                command=["sleep", "30"],
            )
            assert container_id is not None
            assert isinstance(container_id, str)
        finally:
            # Cleanup
            docker_manager.remove_container(test_container_name, force=True)

    def test_start_container(self, docker_manager, test_container_name):
        """Starting a container should succeed."""
        try:
            docker_manager.create_container(
                image="alpine:latest",
                name=test_container_name,
                command=["sleep", "30"],
            )
            result = docker_manager.start_container(test_container_name)
            assert result is True

            # Verify it's running
            status = docker_manager.get_container_status(test_container_name)
            assert status == "running"
        finally:
            docker_manager.remove_container(test_container_name, force=True)

    def test_stop_container(self, docker_manager, test_container_name):
        """Stopping a container should succeed."""
        try:
            docker_manager.create_container(
                image="alpine:latest",
                name=test_container_name,
                command=["sleep", "30"],
            )
            docker_manager.start_container(test_container_name)
            result = docker_manager.stop_container(test_container_name)
            assert result is True

            status = docker_manager.get_container_status(test_container_name)
            assert status in ["exited", "stopped"]
        finally:
            docker_manager.remove_container(test_container_name, force=True)

    def test_remove_container(self, docker_manager, test_container_name):
        """Removing a container should succeed."""
        docker_manager.create_container(
            image="alpine:latest",
            name=test_container_name,
            command=["sleep", "30"],
        )
        result = docker_manager.remove_container(test_container_name, force=True)
        assert result is True

    def test_get_container_status(self, docker_manager, test_container_name):
        """Getting container status should return valid status."""
        try:
            docker_manager.create_container(
                image="alpine:latest",
                name=test_container_name,
                command=["sleep", "30"],
            )
            status = docker_manager.get_container_status(test_container_name)
            assert status in ["created", "running", "exited", "paused", "restarting", "dead"]
        finally:
            docker_manager.remove_container(test_container_name, force=True)

    def test_get_nonexistent_container_status_returns_none(self, docker_manager):
        """Getting status of nonexistent container should return None."""
        status = docker_manager.get_container_status("nonexistent-container-12345")
        assert status is None


class TestContainerExec:
    """Tests for executing commands in containers."""

    @pytest.fixture
    def running_container(self, docker_manager):
        """Create and start a container for exec tests."""
        name = "test-exec-container"
        try:
            docker_manager.create_container(
                image="alpine:latest",
                name=name,
                command=["sleep", "60"],
            )
            docker_manager.start_container(name)
            yield name
        finally:
            docker_manager.remove_container(name, force=True)

    def test_exec_in_container(self, docker_manager, running_container):
        """Executing a command in container should return output."""
        exit_code, output = docker_manager.exec_in_container(
            running_container,
            ["echo", "hello"]
        )
        assert exit_code == 0
        assert "hello" in output
