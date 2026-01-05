# API Contracts

This project uses shared type definitions to ensure frontend and backend stay synchronized.

## Contract Files

| Language | File | Purpose |
|----------|------|---------|
| Python | `backend/app/models/contracts.py` | Pydantic models (source of truth) |
| TypeScript | `frontend/src/lib/types/api.ts` | TypeScript interfaces |

## Contract Philosophy

1. **Python First** - Define all types in `contracts.py`
2. **TypeScript Mirrors** - `api.ts` must match Python exactly
3. **Frozen After Phase 0** - No breaking changes without coordination
4. **Test Verified** - Contract tests ensure serialization works

## Type Definitions

### Enums

```python
# Python
class ContainerStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    EXITED = "exited"
    ERROR = "error"
```

```typescript
// TypeScript
export type ContainerStatus = 'created' | 'running' | 'exited' | 'error';
```

### Status Enums

| Enum | Values | Usage |
|------|--------|-------|
| ContainerStatus | created, running, exited, error | Docker container state |
| WorkflowStatus | pending, running, paused, completed, failed, cancelled | Workflow execution state |
| TerminalMessageType | output, input, system, error | WebSocket message classification |
| TerminalCommandType | input, interrupt, resize | Client command types |

### Project Models

```python
# CreateProject - Request to create a project
class CreateProject(BaseModel):
    name: str
    path: str = ""
    scaffold: bool = True
    github_private: bool = True

# Project - Full project record
class Project(BaseModel):
    id: str
    name: str
    path: str
    created_at: datetime
    container_id: str | None = None
    github_url: str | None = None
```

```typescript
// TypeScript equivalents
export interface CreateProject {
  name: string;
  path?: string;
  scaffold?: boolean;
  github_private?: boolean;
}

export interface Project {
  id: string;
  name: string;
  path: string;
  created_at: string;  // ISO 8601
  container_id?: string;
  github_url?: string;
}
```

### Container Models

```python
class Container(BaseModel):
    id: str
    project_id: str
    status: ContainerStatus
    created_at: datetime
    image: str = "claude-cli:latest"
```

### Terminal Models

```python
# Server -> Client messages
class TerminalMessage(BaseModel):
    type: TerminalMessageType
    data: str
    timestamp: datetime

# Client -> Server commands
class TerminalCommand(BaseModel):
    type: TerminalCommandType
    data: str | None = None

# Resize command
class TerminalResize(BaseModel):
    cols: int
    rows: int
```

### Workflow Models

```python
class WorkflowStep(BaseModel):
    name: str
    command: str
    review_after: bool = False
    timeout_seconds: int = 300

class Workflow(BaseModel):
    id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    loop_count: int = 1
    max_review_iterations: int = 5

class WorkflowExecution(BaseModel):
    id: str
    workflow_id: str
    project_id: str
    status: WorkflowStatus
    current_step: int
    current_loop: int
    review_iteration: int
    started_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None
```

### Response Wrappers

```python
class ProjectList(BaseModel):
    projects: list[Project]
    total: int

class ContainerList(BaseModel):
    containers: list[Container]
    total: int

class WorkflowList(BaseModel):
    workflows: list[Workflow]
    total: int

class HealthCheck(BaseModel):
    status: str
    docker_available: bool
    version: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict | None = None
```

## Type Mappings

| Python | TypeScript | JSON | Notes |
|--------|------------|------|-------|
| `str` | `string` | `string` | |
| `int` | `number` | `number` | |
| `float` | `number` | `number` | |
| `bool` | `boolean` | `boolean` | |
| `datetime` | `string` | `string` | ISO 8601 format |
| `list[T]` | `T[]` | `array` | |
| `dict` | `Record<string, unknown>` | `object` | |
| `T \| None` | `T \| undefined` | nullable | |
| `Enum` | Union type | `string` | `'a' \| 'b'` |

## Datetime Serialization

All datetime fields serialize to ISO 8601 strings:

```python
# Python
created_at: datetime  # 2024-01-01T00:00:00Z

# JSON
"created_at": "2024-01-01T00:00:00Z"

# TypeScript (after JSON.parse)
created_at: string  // "2024-01-01T00:00:00Z"
```

## Breaking Change Policy

### What Constitutes a Breaking Change

1. Removing a field
2. Changing a field's type
3. Making an optional field required
4. Changing enum values
5. Changing field names

### How to Make Changes

1. **Coordinate** - Discuss with frontend/backend teams
2. **Update Python** - Modify `contracts.py`
3. **Update TypeScript** - Mirror changes in `api.ts`
4. **Run Tests** - `pytest tests/contracts/ -v`
5. **Update Docs** - Update this file

### Non-Breaking Changes

These can be made safely:

1. Adding new optional fields
2. Adding new endpoints
3. Adding new enum values (if clients handle unknown)

## Contract Tests

Located in `backend/tests/contracts/test_contracts.py`:

```bash
# Run contract tests
cd backend
uv run pytest tests/contracts/ -v
```

Tests verify:

- Enum values match expected strings
- Models serialize/deserialize correctly
- JSON round-trip maintains data integrity
- Validation constraints enforced
- Datetime serialization as ISO 8601

## Type Guards (TypeScript)

The frontend includes runtime type guards:

```typescript
export function isContainerStatus(value: unknown): value is ContainerStatus {
  return typeof value === 'string' &&
    ['created', 'running', 'exited', 'error'].includes(value);
}

export function isWorkflowStatus(value: unknown): value is WorkflowStatus {
  return typeof value === 'string' &&
    ['pending', 'running', 'paused', 'completed', 'failed', 'cancelled'].includes(value);
}
```

Use these when parsing API responses to ensure type safety at runtime.

## Adding New Types

1. Define in Python first:

```python
# backend/app/models/contracts.py
class NewModel(BaseModel):
    field: str
    optional_field: int | None = None
```

2. Mirror in TypeScript:

```typescript
// frontend/src/lib/types/api.ts
export interface NewModel {
  field: string;
  optional_field?: number;
}
```

3. Add contract tests:

```python
# backend/tests/contracts/test_contracts.py
class TestNewModel:
    def test_creates_with_required_field(self):
        model = NewModel(field="value")
        assert model.field == "value"

    def test_json_round_trip(self):
        model = NewModel(field="value", optional_field=42)
        json_str = model.model_dump_json()
        restored = NewModel.model_validate_json(json_str)
        assert model == restored
```

4. Update this documentation

## Versioning

Current version: **1.0.0** (frozen)

Version history:

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-01 | Initial contract freeze |
