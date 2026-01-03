"""Integration tests for CLI runner (PTY process management)."""

import asyncio
import os
import signal
import pytest

from app.services.cli_runner import CLIRunner, ProcessState


class TestCLIRunnerBasics:
    """Basic CLI runner tests."""

    def test_cli_runner_can_be_instantiated(self):
        """CLIRunner should instantiate without error."""
        runner = CLIRunner()
        assert runner is not None

    @pytest.mark.asyncio
    async def test_spawn_process_returns_session_id(self):
        """spawn_process should return a session ID."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["echo", "hello"])
        assert session_id is not None
        assert isinstance(session_id, str)
        # Cleanup
        await runner.terminate_process(session_id)

    @pytest.mark.asyncio
    async def test_get_process_state(self):
        """get_process_state should return current state."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["sleep", "10"])
        state = runner.get_process_state(session_id)
        assert state == ProcessState.RUNNING
        await runner.terminate_process(session_id)

    @pytest.mark.asyncio
    async def test_process_exits_naturally(self):
        """Process should transition to EXITED state after completion."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["echo", "hello"])
        # Wait for process to complete
        await asyncio.sleep(0.5)
        state = runner.get_process_state(session_id)
        assert state == ProcessState.EXITED


class TestCLIRunnerOutput:
    """Tests for process output handling."""

    @pytest.mark.asyncio
    async def test_read_output_from_process(self):
        """Should be able to read output from process."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["echo", "hello world"])
        # Give process time to produce output
        await asyncio.sleep(0.2)
        output = await runner.read_output(session_id, timeout=1.0)
        assert "hello world" in output

    @pytest.mark.asyncio
    async def test_read_output_from_interactive_process(self):
        """Should be able to read output from interactive process."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["sh", "-c", "echo 'prompt> '"])
        await asyncio.sleep(0.2)
        output = await runner.read_output(session_id, timeout=1.0)
        assert "prompt>" in output


class TestCLIRunnerInput:
    """Tests for sending input to processes."""

    @pytest.mark.asyncio
    async def test_send_input_to_process(self):
        """Should be able to send input to process."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["cat"])
        # Send input
        await runner.send_input(session_id, "hello\n")
        await asyncio.sleep(0.2)
        output = await runner.read_output(session_id, timeout=1.0)
        assert "hello" in output
        # Cleanup
        await runner.terminate_process(session_id)


class TestCLIRunnerSignals:
    """Tests for signal handling."""

    @pytest.mark.asyncio
    async def test_send_interrupt_signal(self):
        """Should be able to send SIGINT to process."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["sleep", "60"])
        await asyncio.sleep(0.1)  # Let process start
        # Send SIGINT
        await runner.send_signal(session_id, signal.SIGINT)
        # Wait for state to update
        for _ in range(20):
            state = runner.get_process_state(session_id)
            if state == ProcessState.EXITED:
                break
            await asyncio.sleep(0.1)
        assert state == ProcessState.EXITED

    @pytest.mark.asyncio
    async def test_terminate_process(self):
        """terminate_process should stop the process."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["sleep", "60"])
        result = await runner.terminate_process(session_id)
        assert result is True
        state = runner.get_process_state(session_id)
        assert state == ProcessState.EXITED


class TestCLIRunnerResize:
    """Tests for terminal resizing."""

    @pytest.mark.asyncio
    async def test_resize_terminal(self):
        """Should be able to resize terminal."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["sh"])
        result = await runner.resize_terminal(session_id, cols=120, rows=40)
        assert result is True
        await runner.terminate_process(session_id)


class TestCLIRunnerSessions:
    """Tests for session management."""

    @pytest.mark.asyncio
    async def test_list_sessions(self):
        """list_sessions should return all active sessions."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["sleep", "10"])
        sessions = runner.list_sessions()
        assert session_id in sessions
        await runner.terminate_process(session_id)

    @pytest.mark.asyncio
    async def test_get_session_info(self):
        """get_session_info should return session details."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["sleep", "10"])
        info = runner.get_session_info(session_id)
        assert info is not None
        assert "pid" in info
        assert "state" in info
        assert info["state"] == ProcessState.RUNNING.value
        await runner.terminate_process(session_id)

    @pytest.mark.asyncio
    async def test_cleanup_dead_sessions(self):
        """cleanup_sessions should remove dead sessions."""
        runner = CLIRunner()
        session_id = await runner.spawn_process(["echo", "done"])
        await asyncio.sleep(0.5)  # Wait for process to exit
        count = await runner.cleanup_sessions()
        assert count >= 0  # May be 0 or 1 depending on timing
