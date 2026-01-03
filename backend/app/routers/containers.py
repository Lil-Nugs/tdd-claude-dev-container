"""Container management router."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.docker_manager import DockerManager

router = APIRouter(prefix="/api", tags=["containers"])

# Global docker manager instance
docker_manager = DockerManager()


class ContainerCreate(BaseModel):
    """Schema for creating a container."""

    image: str
    name: str
    command: Optional[list[str]] = None
    environment: Optional[dict[str, str]] = None
    volumes: Optional[dict[str, dict[str, str]]] = None
    ports: Optional[dict[str, int]] = None


class ContainerResponse(BaseModel):
    """Schema for container response."""

    id: str
    name: str
    status: str
    image: Optional[str] = None


class StatusResponse(BaseModel):
    """Simple status response."""

    status: str


@router.get("/containers", response_model=list[dict[str, Any]])
def list_containers(all_containers: bool = False) -> list[dict[str, Any]]:
    """List all containers."""
    return docker_manager.list_containers(all_containers=all_containers)


@router.get("/containers/{container_id}", response_model=ContainerResponse)
def get_container(container_id: str) -> ContainerResponse:
    """Get container details."""
    container_status = docker_manager.get_container_status(container_id)
    if container_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found",
        )
    return ContainerResponse(
        id=container_id,
        name=container_id,
        status=container_status,
    )


@router.post("/containers", response_model=ContainerResponse, status_code=status.HTTP_201_CREATED)
def create_container(container: ContainerCreate) -> ContainerResponse:
    """Create a new container."""
    try:
        container_id = docker_manager.create_container(
            image=container.image,
            name=container.name,
            command=container.command,
            environment=container.environment,
            volumes=container.volumes,
            ports=container.ports,
        )
        return ContainerResponse(
            id=container_id,
            name=container.name,
            status="created",
            image=container.image,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/containers/{container_id}/start", response_model=StatusResponse)
def start_container(container_id: str) -> StatusResponse:
    """Start a container."""
    success = docker_manager.start_container(container_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found or failed to start",
        )
    return StatusResponse(status="started")


@router.post("/containers/{container_id}/stop", response_model=StatusResponse)
def stop_container(container_id: str, timeout: int = 10) -> StatusResponse:
    """Stop a container."""
    success = docker_manager.stop_container(container_id, timeout=timeout)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found or failed to stop",
        )
    return StatusResponse(status="stopped")


@router.delete("/containers/{container_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_container(container_id: str, force: bool = False) -> None:
    """Delete a container."""
    success = docker_manager.remove_container(container_id, force=force)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container {container_id} not found or failed to remove",
        )


@router.get("/images", response_model=list[dict[str, Any]])
def list_images() -> list[dict[str, Any]]:
    """List all images."""
    return docker_manager.list_images()
