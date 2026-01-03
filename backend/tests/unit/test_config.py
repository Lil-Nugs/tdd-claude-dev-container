"""Tests for configuration settings."""

import pytest

from app.config import Settings


def test_settings_default_values():
    """Settings should have sensible defaults."""
    settings = Settings()
    assert settings.app_name == "tdd-claude-dev-container"
    assert settings.debug is False
    assert settings.database_url.startswith("sqlite")


def test_settings_database_url_default():
    """Default database URL should be SQLite."""
    settings = Settings()
    assert "sqlite" in settings.database_url


def test_settings_docker_socket():
    """Docker socket path should be configurable."""
    settings = Settings()
    assert settings.docker_socket == "unix:///var/run/docker.sock"
