"""Docker SDK wrapper for container management."""

from typing import Any

import docker
from docker.errors import NotFound, APIError

from app.config import settings


class DockerManager:
    """Manages Docker containers using the Docker SDK."""

    def __init__(self, socket_url: str | None = None):
        """Initialize Docker client.

        Args:
            socket_url: Docker socket URL. Defaults to settings.docker_socket.
        """
        self._socket_url = socket_url or settings.docker_socket
        self._client = None

    @property
    def client(self) -> docker.DockerClient:
        """Lazy-loaded Docker client."""
        if self._client is None:
            self._client = docker.from_env()
        return self._client

    def ping(self) -> bool:
        """Check if Docker daemon is accessible.

        Returns:
            True if Docker is accessible, False otherwise.
        """
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def list_containers(self, all_containers: bool = False) -> list[dict[str, Any]]:
        """List Docker containers.

        Args:
            all_containers: If True, include stopped containers.

        Returns:
            List of container information dicts.
        """
        containers = self.client.containers.list(all=all_containers)
        return [
            {
                "id": c.id,
                "short_id": c.short_id,
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else c.image.id,
            }
            for c in containers
        ]

    def list_images(self) -> list[dict[str, Any]]:
        """List Docker images.

        Returns:
            List of image information dicts.
        """
        images = self.client.images.list()
        return [
            {
                "id": img.id,
                "short_id": img.short_id,
                "tags": img.tags,
            }
            for img in images
        ]

    def create_container(
        self,
        image: str,
        name: str,
        command: list[str] | None = None,
        environment: dict[str, str] | None = None,
        volumes: dict[str, dict[str, str]] | None = None,
        ports: dict[str, int] | None = None,
        **kwargs: Any,
    ) -> str:
        """Create a new container.

        Args:
            image: Docker image to use.
            name: Container name.
            command: Command to run in container.
            environment: Environment variables.
            volumes: Volume mappings.
            ports: Port mappings.
            **kwargs: Additional arguments passed to Docker API.

        Returns:
            Container ID.
        """
        # Pull image if not present
        try:
            self.client.images.get(image)
        except NotFound:
            self.client.images.pull(image)

        container = self.client.containers.create(
            image=image,
            name=name,
            command=command,
            environment=environment,
            volumes=volumes,
            ports=ports,
            detach=True,
            **kwargs,
        )
        return container.id

    def start_container(self, name_or_id: str) -> bool:
        """Start a container.

        Args:
            name_or_id: Container name or ID.

        Returns:
            True if successful.
        """
        try:
            container = self.client.containers.get(name_or_id)
            container.start()
            return True
        except (NotFound, APIError):
            return False

    def stop_container(self, name_or_id: str, timeout: int = 10) -> bool:
        """Stop a container.

        Args:
            name_or_id: Container name or ID.
            timeout: Seconds to wait before killing.

        Returns:
            True if successful.
        """
        try:
            container = self.client.containers.get(name_or_id)
            container.stop(timeout=timeout)
            return True
        except (NotFound, APIError):
            return False

    def remove_container(self, name_or_id: str, force: bool = False) -> bool:
        """Remove a container.

        Args:
            name_or_id: Container name or ID.
            force: Force removal of running container.

        Returns:
            True if successful.
        """
        try:
            container = self.client.containers.get(name_or_id)
            container.remove(force=force)
            return True
        except NotFound:
            return True  # Already removed
        except APIError:
            return False

    def get_container_status(self, name_or_id: str) -> str | None:
        """Get container status.

        Args:
            name_or_id: Container name or ID.

        Returns:
            Status string or None if container not found.
        """
        try:
            container = self.client.containers.get(name_or_id)
            container.reload()
            return container.status
        except NotFound:
            return None

    def exec_in_container(
        self,
        name_or_id: str,
        command: list[str],
        workdir: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> tuple[int, str]:
        """Execute a command in a running container.

        Args:
            name_or_id: Container name or ID.
            command: Command to execute.
            workdir: Working directory for command.
            environment: Environment variables.

        Returns:
            Tuple of (exit_code, output).
        """
        container = self.client.containers.get(name_or_id)
        result = container.exec_run(
            cmd=command,
            workdir=workdir,
            environment=environment,
        )
        return result.exit_code, result.output.decode("utf-8")

    def get_container_logs(
        self,
        name_or_id: str,
        tail: int = 100,
        since: int | None = None,
    ) -> str:
        """Get container logs.

        Args:
            name_or_id: Container name or ID.
            tail: Number of lines to return from end.
            since: Unix timestamp to get logs since.

        Returns:
            Container logs as string.
        """
        container = self.client.containers.get(name_or_id)
        logs = container.logs(
            tail=tail,
            since=since,
            timestamps=True,
        )
        return logs.decode("utf-8")
