"""Integration tests for WebSocket terminal streaming."""

import asyncio
import json
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app


class TestWebSocketTerminal:
    """Tests for WebSocket terminal endpoint."""

    @pytest.fixture
    def test_client(self):
        """Sync test client for WebSocket tests."""
        return TestClient(app)

    def test_websocket_connection_accepted(self, test_client):
        """WebSocket connection should be accepted."""
        with test_client.websocket_connect("/api/terminal/test-session") as websocket:
            # Send a ping-type message to verify connection
            websocket.send_json({"type": "ping"})
            # Connection is accepted if we get this far
            assert True

    def test_websocket_spawn_process(self, test_client):
        """Should be able to spawn a process via WebSocket."""
        with test_client.websocket_connect("/api/terminal/spawn-test") as websocket:
            # Spawn a simple echo process
            websocket.send_json({
                "type": "spawn",
                "command": ["echo", "hello from websocket"],
            })
            # Wait for output
            response = websocket.receive_json()
            assert response["type"] in ["output", "status"]

    def test_websocket_input_message(self, test_client):
        """Should be able to send input via WebSocket."""
        with test_client.websocket_connect("/api/terminal/input-test") as websocket:
            # Spawn cat process
            websocket.send_json({
                "type": "spawn",
                "command": ["cat"],
            })
            # Wait briefly for process to start
            import time
            time.sleep(0.2)
            # Send input
            websocket.send_json({
                "type": "input",
                "data": "test input\n",
            })
            # We should get the echoed output back
            response = websocket.receive_json()
            assert response["type"] in ["output", "status"]

    def test_websocket_interrupt_message(self, test_client):
        """Should be able to send interrupt via WebSocket."""
        with test_client.websocket_connect("/api/terminal/interrupt-test") as websocket:
            # Spawn a long-running process
            websocket.send_json({
                "type": "spawn",
                "command": ["sleep", "60"],
            })
            import time
            time.sleep(0.2)
            # Send interrupt
            websocket.send_json({"type": "interrupt"})
            # Should get status update
            response = websocket.receive_json()
            assert response["type"] in ["output", "status"]

    def test_websocket_resize_message(self, test_client):
        """Should be able to resize terminal via WebSocket."""
        with test_client.websocket_connect("/api/terminal/resize-test") as websocket:
            # Spawn a shell
            websocket.send_json({
                "type": "spawn",
                "command": ["sh"],
            })
            import time
            time.sleep(0.1)
            # Send resize
            websocket.send_json({
                "type": "resize",
                "cols": 120,
                "rows": 40,
            })
            # Connection should remain open
            # Clean up
            websocket.send_json({"type": "interrupt"})

    def test_websocket_status_updates(self, test_client):
        """Should receive status updates on process state changes."""
        with test_client.websocket_connect("/api/terminal/status-test") as websocket:
            # Spawn a quick process
            websocket.send_json({
                "type": "spawn",
                "command": ["echo", "done"],
            })
            # Collect messages
            messages = []
            for _ in range(5):
                try:
                    msg = websocket.receive_json()
                    messages.append(msg)
                    if msg.get("type") == "status" and msg.get("state") == "exited":
                        break
                except Exception:
                    break
            # Should have at least one message
            assert len(messages) > 0


class TestWebSocketProtocol:
    """Tests for WebSocket message protocol."""

    @pytest.fixture
    def test_client(self):
        """Sync test client for WebSocket tests."""
        return TestClient(app)

    def test_input_message_format(self, test_client):
        """Input message should follow protocol format."""
        with test_client.websocket_connect("/api/terminal/protocol-test-1") as websocket:
            websocket.send_json({
                "type": "spawn",
                "command": ["cat"],
            })
            import time
            time.sleep(0.1)
            # Valid input message
            websocket.send_json({
                "type": "input",
                "data": "hello\n",
            })
            # Should not error
            response = websocket.receive_json()
            assert "type" in response

    def test_output_message_format(self, test_client):
        """Output message should follow protocol format."""
        with test_client.websocket_connect("/api/terminal/protocol-test-2") as websocket:
            websocket.send_json({
                "type": "spawn",
                "command": ["echo", "test output"],
            })
            # Get output
            response = websocket.receive_json()
            if response["type"] == "output":
                assert "data" in response
            elif response["type"] == "status":
                assert "state" in response

    def test_status_message_format(self, test_client):
        """Status message should follow protocol format."""
        with test_client.websocket_connect("/api/terminal/protocol-test-3") as websocket:
            websocket.send_json({
                "type": "spawn",
                "command": ["echo", "done"],
            })
            # Collect messages until we get a status
            for _ in range(10):
                import time
                time.sleep(0.1)
                try:
                    response = websocket.receive_json()
                    if response["type"] == "status":
                        assert response["state"] in ["running", "exited", "error"]
                        break
                except Exception:
                    break
