"""PTY process management for terminal sessions."""

import asyncio
import fcntl
import os
import pty
import signal
import struct
import termios
import uuid
from enum import Enum
from typing import Any


class ProcessState(Enum):
    """State of a managed process."""

    PENDING = "pending"
    RUNNING = "running"
    EXITED = "exited"
    ERROR = "error"


class ProcessSession:
    """Represents a PTY process session."""

    def __init__(self, pid: int, fd: int, command: list[str]):
        """Initialize a process session.

        Args:
            pid: Process ID.
            fd: PTY file descriptor.
            command: Command that was executed.
        """
        self.pid = pid
        self.fd = fd
        self.command = command
        self.state = ProcessState.RUNNING
        self.exit_code: int | None = None
        self._output_buffer = b""

    def to_dict(self) -> dict[str, Any]:
        """Convert session info to dictionary."""
        return {
            "pid": self.pid,
            "fd": self.fd,
            "command": self.command,
            "state": self.state.value,
            "exit_code": self.exit_code,
        }


class CLIRunner:
    """Manages PTY processes for terminal sessions."""

    def __init__(self):
        """Initialize the CLI runner."""
        self._sessions: dict[str, ProcessSession] = {}

    async def spawn_process(
        self,
        command: list[str],
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> str:
        """Spawn a new process with PTY.

        Args:
            command: Command and arguments to execute.
            cwd: Working directory for the process.
            env: Environment variables.

        Returns:
            Session ID for the process.
        """
        session_id = str(uuid.uuid4())

        # Prepare environment
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        # Fork with PTY
        pid, fd = pty.fork()

        if pid == 0:
            # Child process
            if cwd:
                os.chdir(cwd)
            os.execvpe(command[0], command, process_env)
        else:
            # Parent process
            # Set non-blocking mode on the fd
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            session = ProcessSession(pid, fd, command)
            self._sessions[session_id] = session

            # Start background task to monitor process
            asyncio.create_task(self._monitor_process(session_id))

        return session_id

    async def _monitor_process(self, session_id: str) -> None:
        """Monitor process for state changes and buffer output."""
        session = self._sessions.get(session_id)
        if not session:
            return

        while session.state == ProcessState.RUNNING:
            # Read any available output into buffer
            try:
                chunk = os.read(session.fd, 4096)
                if chunk:
                    session._output_buffer += chunk
            except BlockingIOError:
                pass
            except OSError:
                pass

            try:
                # Check if process has exited
                pid, status = os.waitpid(session.pid, os.WNOHANG)
                if pid != 0:
                    # Read any remaining output before marking exited
                    try:
                        while True:
                            chunk = os.read(session.fd, 4096)
                            if chunk:
                                session._output_buffer += chunk
                            else:
                                break
                    except (BlockingIOError, OSError):
                        pass

                    session.state = ProcessState.EXITED
                    if os.WIFEXITED(status):
                        session.exit_code = os.WEXITSTATUS(status)
                    elif os.WIFSIGNALED(status):
                        session.exit_code = -os.WTERMSIG(status)
                    break
            except ChildProcessError:
                session.state = ProcessState.EXITED
                break
            await asyncio.sleep(0.05)

    def get_process_state(self, session_id: str) -> ProcessState | None:
        """Get the state of a process.

        Args:
            session_id: Session ID.

        Returns:
            Process state or None if not found.
        """
        session = self._sessions.get(session_id)
        if session:
            # Quick check if process is still alive
            if session.state == ProcessState.RUNNING:
                try:
                    pid, status = os.waitpid(session.pid, os.WNOHANG)
                    if pid != 0:
                        session.state = ProcessState.EXITED
                        if os.WIFEXITED(status):
                            session.exit_code = os.WEXITSTATUS(status)
                except ChildProcessError:
                    session.state = ProcessState.EXITED
            return session.state
        return None

    async def read_output(
        self,
        session_id: str,
        timeout: float = 0.1,
        max_bytes: int = 4096,
    ) -> str:
        """Read output from process.

        Args:
            session_id: Session ID.
            timeout: Timeout in seconds.
            max_bytes: Maximum bytes to read.

        Returns:
            Output string.
        """
        session = self._sessions.get(session_id)
        if not session:
            return ""

        output = b""

        # First drain the buffer
        if session._output_buffer:
            output = session._output_buffer
            session._output_buffer = b""

        # If process is still running, try to read more
        if session.state == ProcessState.RUNNING:
            deadline = asyncio.get_event_loop().time() + timeout

            while asyncio.get_event_loop().time() < deadline:
                try:
                    chunk = os.read(session.fd, max_bytes)
                    if chunk:
                        output += chunk
                    else:
                        break
                except BlockingIOError:
                    if output:
                        break  # We have some output, return it
                    await asyncio.sleep(0.01)
                except OSError:
                    break

        return output.decode("utf-8", errors="replace")

    async def send_input(self, session_id: str, data: str) -> bool:
        """Send input to process.

        Args:
            session_id: Session ID.
            data: Input data to send.

        Returns:
            True if successful.
        """
        session = self._sessions.get(session_id)
        if not session or session.state != ProcessState.RUNNING:
            return False

        try:
            os.write(session.fd, data.encode("utf-8"))
            return True
        except OSError:
            return False

    async def send_signal(self, session_id: str, sig: signal.Signals) -> bool:
        """Send signal to process.

        Args:
            session_id: Session ID.
            sig: Signal to send.

        Returns:
            True if successful.
        """
        session = self._sessions.get(session_id)
        if not session or session.state != ProcessState.RUNNING:
            return False

        try:
            os.kill(session.pid, sig)
            return True
        except OSError:
            return False

    async def terminate_process(self, session_id: str, force: bool = False) -> bool:
        """Terminate a process.

        Args:
            session_id: Session ID.
            force: If True, use SIGKILL instead of SIGTERM.

        Returns:
            True if successful.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        if session.state == ProcessState.RUNNING:
            sig = signal.SIGKILL if force else signal.SIGTERM
            try:
                os.kill(session.pid, sig)
                # Wait for process to exit
                await asyncio.sleep(0.2)
                try:
                    os.waitpid(session.pid, os.WNOHANG)
                except ChildProcessError:
                    pass
                session.state = ProcessState.EXITED
            except OSError:
                pass

            try:
                os.close(session.fd)
            except OSError:
                pass

        return True

    async def resize_terminal(
        self,
        session_id: str,
        cols: int,
        rows: int,
    ) -> bool:
        """Resize the terminal.

        Args:
            session_id: Session ID.
            cols: Number of columns.
            rows: Number of rows.

        Returns:
            True if successful.
        """
        session = self._sessions.get(session_id)
        if not session or session.state != ProcessState.RUNNING:
            return False

        try:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(session.fd, termios.TIOCSWINSZ, winsize)
            return True
        except OSError:
            return False

    def list_sessions(self) -> list[str]:
        """List all session IDs.

        Returns:
            List of session IDs.
        """
        return list(self._sessions.keys())

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """Get session information.

        Args:
            session_id: Session ID.

        Returns:
            Session info dict or None.
        """
        session = self._sessions.get(session_id)
        if session:
            return session.to_dict()
        return None

    async def cleanup_sessions(self) -> int:
        """Clean up dead sessions.

        Returns:
            Number of sessions cleaned up.
        """
        dead_sessions = []
        for session_id, session in self._sessions.items():
            if session.state == ProcessState.EXITED:
                dead_sessions.append(session_id)

        for session_id in dead_sessions:
            del self._sessions[session_id]

        return len(dead_sessions)
