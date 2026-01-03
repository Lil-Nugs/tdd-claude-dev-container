"""Tests for health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok(client):
    """Health endpoint should return status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_endpoint_includes_docker_status(client):
    """Health endpoint should include Docker connection status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "docker" in data
    assert data["docker"] in ["connected", "disconnected"]
