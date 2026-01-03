"""Tests for containers router."""

import pytest


class TestContainersRouter:
    """Tests for container endpoints."""

    @pytest.mark.asyncio
    async def test_list_containers(self, client):
        """GET /api/containers should list containers."""
        response = await client.get("/api/containers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_container_not_found(self, client):
        """GET /api/containers/{id} should return 404 for nonexistent container."""
        response = await client.get("/api/containers/nonexistent-container-12345")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_images(self, client):
        """GET /api/images should list images."""
        response = await client.get("/api/images")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestContainerLifecycleEndpoints:
    """Tests for container lifecycle endpoints."""

    @pytest.fixture
    def container_create_payload(self):
        """Payload for creating a test container."""
        return {
            "image": "alpine:latest",
            "name": "test-api-container",
            "command": ["sleep", "30"],
        }

    @pytest.mark.asyncio
    async def test_create_container(self, client, container_create_payload):
        """POST /api/containers should create a container."""
        response = await client.post(
            "/api/containers",
            json=container_create_payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == container_create_payload["name"]

        # Cleanup
        await client.delete(
            f"/api/containers/{container_create_payload['name']}",
            params={"force": True}
        )

    @pytest.mark.asyncio
    async def test_start_container(self, client, container_create_payload):
        """POST /api/containers/{id}/start should start a container."""
        # Create container first
        create_response = await client.post(
            "/api/containers",
            json=container_create_payload,
        )
        container_name = container_create_payload["name"]

        try:
            response = await client.post(f"/api/containers/{container_name}/start")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "started"
        finally:
            # Cleanup
            await client.delete(
                f"/api/containers/{container_name}",
                params={"force": True}
            )

    @pytest.mark.asyncio
    async def test_stop_container(self, client, container_create_payload):
        """POST /api/containers/{id}/stop should stop a container."""
        # Create and start container
        await client.post("/api/containers", json=container_create_payload)
        container_name = container_create_payload["name"]
        await client.post(f"/api/containers/{container_name}/start")

        try:
            response = await client.post(f"/api/containers/{container_name}/stop")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "stopped"
        finally:
            await client.delete(
                f"/api/containers/{container_name}",
                params={"force": True}
            )

    @pytest.mark.asyncio
    async def test_delete_container(self, client, container_create_payload):
        """DELETE /api/containers/{id} should delete a container."""
        await client.post("/api/containers", json=container_create_payload)
        container_name = container_create_payload["name"]

        response = await client.delete(
            f"/api/containers/{container_name}",
            params={"force": True}
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_get_container_status(self, client, container_create_payload):
        """GET /api/containers/{id} should return container status."""
        await client.post("/api/containers", json=container_create_payload)
        container_name = container_create_payload["name"]

        try:
            response = await client.get(f"/api/containers/{container_name}")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] in ["created", "running", "exited", "paused"]
        finally:
            await client.delete(
                f"/api/containers/{container_name}",
                params={"force": True}
            )
