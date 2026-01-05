# API Documentation

Complete API reference for the TDD Claude Dev Container backend.

## Base URL

- Development: `http://localhost:8000`
- Production: Configure via environment

## Authentication

Currently no authentication required. Configure CORS settings in `app/main.py` for production.

---

## Health Check

### GET /health

Check API and Docker connectivity status.

**Response:**
```json
{
  "status": "healthy",
  "docker": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | string | Always "healthy" if responding |
| docker | boolean | Docker daemon connectivity |

---

## Projects

### GET /api/projects

List all projects with pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of records to skip |
| limit | integer | 100 | Maximum records to return |

**Response:** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "my-project",
    "description": "Project description",
    "github_url": null,
    "local_path": "/projects/my-project",
    "container_id": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### POST /api/projects

Create a new project.

**Request:**
```json
{
  "name": "my-project",
  "description": "Optional description"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Project name |
| description | string | No | Project description |

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-project",
  "description": "Optional description",
  "github_url": null,
  "local_path": null,
  "container_id": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### GET /api/projects/{project_id}

Get a specific project by ID.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string (UUID) | Project identifier |

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-project",
  "description": null,
  "github_url": null,
  "local_path": "/projects/my-project",
  "container_id": "abc123",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Project does not exist

---

### PATCH /api/projects/{project_id}

Update project fields.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string (UUID) | Project identifier |

**Request:**
```json
{
  "name": "new-name",
  "description": "Updated description",
  "github_url": "https://github.com/org/repo",
  "local_path": "/new/path"
}
```

All fields are optional; only provided fields are updated.

**Response:** `200 OK` - Returns updated project

**Errors:**
- `404 Not Found` - Project does not exist

---

### DELETE /api/projects/{project_id}

Delete a project.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string (UUID) | Project identifier |

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` - Project does not exist

---

## Containers

### GET /api/containers

List Docker containers.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| all_containers | boolean | false | Include stopped containers |

**Response:** `200 OK`
```json
[
  {
    "id": "abc123def456...",
    "short_id": "abc123d",
    "name": "project-container",
    "status": "running",
    "image": "claude-cli:latest"
  }
]
```

---

### GET /api/containers/{container_id}

Get container details.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| container_id | string | Container ID or name |

**Response:** `200 OK`
```json
{
  "id": "abc123def456...",
  "name": "project-container",
  "status": "running",
  "image": "claude-cli:latest"
}
```

**Errors:**
- `404 Not Found` - Container does not exist

---

### POST /api/containers

Create a new container.

**Request:**
```json
{
  "image": "claude-cli:latest",
  "name": "my-container",
  "command": ["/bin/bash"],
  "environment": {
    "ENV_VAR": "value"
  },
  "volumes": {
    "/host/path": {
      "bind": "/container/path",
      "mode": "rw"
    }
  },
  "ports": {
    "8080/tcp": 8080
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| image | string | Yes | Docker image name |
| name | string | No | Container name |
| command | array | No | Command to run |
| environment | object | No | Environment variables |
| volumes | object | No | Volume mounts |
| ports | object | No | Port mappings |

**Response:** `201 Created`
```json
{
  "id": "abc123def456...",
  "name": "my-container",
  "status": "created",
  "image": "claude-cli:latest"
}
```

---

### POST /api/containers/{container_id}/start

Start a stopped container.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| container_id | string | Container ID or name |

**Response:** `200 OK`
```json
{
  "status": "started"
}
```

**Errors:**
- `404 Not Found` - Container does not exist
- `500 Internal Server Error` - Failed to start

---

### POST /api/containers/{container_id}/stop

Stop a running container.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| container_id | string | Container ID or name |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| timeout | integer | 10 | Seconds before force kill |

**Response:** `200 OK`
```json
{
  "status": "stopped"
}
```

**Errors:**
- `404 Not Found` - Container does not exist

---

### DELETE /api/containers/{container_id}

Remove a container.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| container_id | string | Container ID or name |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| force | boolean | false | Force remove running container |

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` - Container does not exist

---

### GET /api/images

List available Docker images.

**Response:** `200 OK`
```json
[
  {
    "id": "sha256:abc123...",
    "short_id": "abc123",
    "tags": ["claude-cli:latest", "claude-cli:v1"]
  }
]
```

---

## WebSocket Terminal

### WS /api/terminal/{session_id}

Establish a WebSocket connection for interactive terminal sessions.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| session_id | string | Unique session identifier (client-generated) |

### Message Protocol

All messages are JSON objects with a `type` field.

#### Client to Server

**Spawn Process:**
```json
{
  "type": "spawn",
  "command": ["bash"],
  "cwd": "/home/user",
  "env": {"TERM": "xterm-256color"}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Must be "spawn" |
| command | array | Yes | Command and arguments |
| cwd | string | No | Working directory |
| env | object | No | Additional environment variables |

**Send Input:**
```json
{
  "type": "input",
  "data": "ls -la\n"
}
```

**Send Interrupt (Ctrl+C):**
```json
{
  "type": "interrupt"
}
```

**Resize Terminal:**
```json
{
  "type": "resize",
  "cols": 80,
  "rows": 24
}
```

**Ping:**
```json
{
  "type": "ping"
}
```

#### Server to Client

**Terminal Output:**
```json
{
  "type": "output",
  "data": "user@host:~$ "
}
```

**Status Update:**
```json
{
  "type": "status",
  "state": "running",
  "exit_code": null
}
```

| state | Description |
|-------|-------------|
| running | Process is active |
| exited | Process terminated normally |
| error | Process terminated with error |

**Pong (response to ping):**
```json
{
  "type": "pong"
}
```

### Security

The terminal enforces security restrictions:

**Allowed Commands:**
- bash, sh
- python, python3
- node, npm, npx
- bd, claude
- git, make
- pytest, ruff, mypy
- pip, uv

**Allowed Working Directories:**
- /home
- /tmp
- /projects
- /workspace

Attempts to use unauthorized commands or paths will result in connection termination.

### Connection Lifecycle

1. Client connects with unique session_id
2. Client sends `spawn` message with command
3. Server creates PTY process and streams output
4. Client sends `input`, `interrupt`, or `resize` as needed
5. Server sends `status` when process state changes
6. Client disconnects or process exits

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "details": {}
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| not_found | 404 | Resource does not exist |
| validation_error | 422 | Invalid request data |
| internal_error | 500 | Server error |
| docker_error | 500 | Docker operation failed |

---

## Rate Limits

No rate limits currently enforced. Consider implementing for production use.

---

## CORS

Development mode allows all origins. Configure `allow_origins` in `app/main.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
