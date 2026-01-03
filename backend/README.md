# TDD Claude Dev Container Backend

FastAPI backend for TDD Claude Dev Container project.

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run server
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/containers` - List containers
- `WS /api/terminal/{session_id}` - Terminal WebSocket
