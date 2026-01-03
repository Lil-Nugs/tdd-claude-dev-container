"""WebSocket endpoint for terminal streaming."""

import asyncio
import signal
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.cli_runner import CLIRunner, ProcessState

router = APIRouter()

# Global CLI runner instance (could be injected via dependency)
cli_runner = CLIRunner()


async def send_output_loop(websocket: WebSocket, session_id: str) -> None:
    """Background task to send output to client."""
    while True:
        state = cli_runner.get_process_state(session_id)
        if state is None:
            break

        # Read and send output
        output = await cli_runner.read_output(session_id, timeout=0.1)
        if output:
            await websocket.send_json({
                "type": "output",
                "data": output,
            })

        # Check if process exited
        if state == ProcessState.EXITED:
            info = cli_runner.get_session_info(session_id)
            await websocket.send_json({
                "type": "status",
                "state": "exited",
                "exit_code": info.get("exit_code") if info else None,
            })
            break

        await asyncio.sleep(0.05)


@router.websocket("/api/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str) -> None:
    """WebSocket endpoint for terminal sessions.

    Protocol:
    - Client messages:
        {"type": "spawn", "command": [...], "cwd": "...", "env": {...}}
        {"type": "input", "data": "..."}
        {"type": "interrupt"}
        {"type": "resize", "cols": 80, "rows": 24}
        {"type": "ping"}

    - Server messages:
        {"type": "output", "data": "..."}
        {"type": "status", "state": "running" | "exited" | "error", "exit_code": ...}
        {"type": "pong"}
    """
    await websocket.accept()

    current_session: str | None = None
    output_task: asyncio.Task | None = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "spawn":
                # Spawn a new process
                command = data.get("command", [])
                cwd = data.get("cwd")
                env = data.get("env")

                if not command:
                    await websocket.send_json({
                        "type": "status",
                        "state": "error",
                        "message": "No command specified",
                    })
                    continue

                # Terminate any existing session
                if current_session:
                    if output_task:
                        output_task.cancel()
                        try:
                            await output_task
                        except asyncio.CancelledError:
                            pass
                    await cli_runner.terminate_process(current_session)

                # Spawn new process
                current_session = await cli_runner.spawn_process(
                    command=command,
                    cwd=cwd,
                    env=env,
                )

                await websocket.send_json({
                    "type": "status",
                    "state": "running",
                    "session_id": current_session,
                })

                # Start output loop
                output_task = asyncio.create_task(
                    send_output_loop(websocket, current_session)
                )

            elif msg_type == "input":
                # Send input to process
                if current_session:
                    input_data = data.get("data", "")
                    await cli_runner.send_input(current_session, input_data)

            elif msg_type == "interrupt":
                # Send SIGINT to process
                if current_session:
                    await cli_runner.send_signal(current_session, signal.SIGINT)

            elif msg_type == "resize":
                # Resize terminal
                if current_session:
                    cols = data.get("cols", 80)
                    rows = data.get("rows", 24)
                    await cli_runner.resize_terminal(current_session, cols, rows)

    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup
        if output_task:
            output_task.cancel()
            try:
                await output_task
            except asyncio.CancelledError:
                pass
        if current_session:
            await cli_runner.terminate_process(current_session)
