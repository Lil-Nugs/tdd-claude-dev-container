"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import Any

import docker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.containers import router as containers_router
from app.routers.projects import router as projects_router
from app.websockets.terminal import router as terminal_router


def check_docker_connection() -> bool:
    """Check if Docker is accessible."""
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    app.state.docker_available = check_docker_connection()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(terminal_router)
app.include_router(projects_router)
app.include_router(containers_router)


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    docker_status = "connected" if check_docker_connection() else "disconnected"
    return {
        "status": "ok",
        "docker": docker_status,
    }
