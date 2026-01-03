"""Tests for projects router."""

import pytest


class TestProjectsRouter:
    """Tests for projects CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_project(self, client):
        """POST /api/projects should create a project."""
        response = await client.post(
            "/api/projects",
            json={
                "name": "test-project",
                "description": "A test project",
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-project"
        assert data["description"] == "A test project"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_projects(self, client):
        """GET /api/projects should list all projects."""
        # Create some projects first
        await client.post("/api/projects", json={"name": "project-1"})
        await client.post("/api/projects", json={"name": "project-2"})

        response = await client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    @pytest.mark.asyncio
    async def test_get_project(self, client):
        """GET /api/projects/{id} should return a project."""
        # Create a project
        create_response = await client.post(
            "/api/projects",
            json={"name": "get-test-project"}
        )
        project_id = create_response.json()["id"]

        response = await client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "get-test-project"
        assert data["id"] == project_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_project(self, client):
        """GET /api/projects/{id} should return 404 for nonexistent project."""
        response = await client.get("/api/projects/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project(self, client):
        """PATCH /api/projects/{id} should update a project."""
        # Create a project
        create_response = await client.post(
            "/api/projects",
            json={"name": "update-test-project"}
        )
        project_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/projects/{project_id}",
            json={"description": "Updated description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["name"] == "update-test-project"

    @pytest.mark.asyncio
    async def test_delete_project(self, client):
        """DELETE /api/projects/{id} should delete a project."""
        # Create a project
        create_response = await client.post(
            "/api/projects",
            json={"name": "delete-test-project"}
        )
        project_id = create_response.json()["id"]

        response = await client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_project(self, client):
        """DELETE /api/projects/{id} should return 404 for nonexistent project."""
        response = await client.delete("/api/projects/99999")
        assert response.status_code == 404
