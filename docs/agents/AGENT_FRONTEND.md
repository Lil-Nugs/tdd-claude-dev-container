# Frontend Agent Instructions

You are the **Frontend Agent** responsible for implementing the SvelteKit PWA frontend.

## Your Domain

You may **ONLY** modify files in:
```
frontend/
```

**DO NOT** touch:
- `backend/` - Backend Agent's domain
- `docker/` - Infrastructure Agent's domain
- `.github/` - Infrastructure Agent's domain
- `docs/` - Shared, coordinate before editing

## Worktree Setup

You are working in a dedicated git worktree:
```bash
# Your worktree location
cd ../tdd-frontend

# Your branch
git branch  # Should show: frontend

# Shared beads database
bd list     # Same issues as other agents
```

## Your Responsibilities

### Phase 5: PWA Frontend - Core UI
- [ ] `frontend/package.json` - Dependencies
- [ ] `frontend/svelte.config.js` - SvelteKit config
- [ ] `frontend/vite.config.ts` - Vite + PWA plugin
- [ ] `frontend/tsconfig.json` - TypeScript config
- [ ] `frontend/src/app.html` - HTML template
- [ ] `frontend/src/routes/+layout.svelte` - Root layout
- [ ] `frontend/src/routes/+page.svelte` - Dashboard
- [ ] `frontend/src/routes/projects/+page.svelte` - Project list
- [ ] `frontend/src/routes/projects/[id]/+page.svelte` - Project detail
- [ ] `frontend/src/routes/projects/[id]/terminal/+page.svelte` - Terminal view
- [ ] `frontend/src/lib/components/Terminal.svelte` - xterm.js wrapper
- [ ] `frontend/src/lib/components/ProjectCard.svelte` - Project display
- [ ] `frontend/src/lib/api/client.ts` - REST API client
- [ ] `frontend/src/lib/api/websocket.ts` - WebSocket connection
- [ ] `frontend/src/lib/types/api.ts` - TypeScript types (from backend contracts)
- [ ] `frontend/static/manifest.json` - PWA manifest
- [ ] `frontend/tests/e2e/projects.spec.ts` - E2E tests

### Phase 7: Frontend Workflow UI
- [ ] `frontend/src/routes/workflows/+page.svelte` - Workflow list
- [ ] `frontend/src/lib/components/WorkflowRunner.svelte` - Workflow execution UI
- [ ] `frontend/src/lib/stores/workflow.ts` - Workflow state
- [ ] `frontend/tests/e2e/workflows.spec.ts` - E2E tests

### Phase 8: Polish & Offline Support
- [ ] `frontend/src/service-worker.ts` - Service worker
- [ ] Error boundaries in components
- [ ] Reconnection logic for WebSocket
- [ ] Offline indicators

## TDD Workflow

**Write tests alongside implementation:**

```bash
# Unit tests
npm run test:unit

# E2E tests (requires backend running)
npm run test:e2e

# Type checking
npm run check
```

## Key Technical Requirements

### Dependencies (package.json)
```json
{
  "devDependencies": {
    "@sveltejs/adapter-static": "^3.0.0",
    "@sveltejs/kit": "^2.0.0",
    "@sveltejs/vite-plugin-svelte": "^3.0.0",
    "svelte": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "@playwright/test": "^1.40.0",
    "vitest": "^1.0.0"
  },
  "dependencies": {
    "xterm": "^5.3.0",
    "xterm-addon-fit": "^0.8.0",
    "xterm-addon-web-links": "^0.9.0"
  }
}
```

### Terminal Component Structure
```svelte
<!-- Terminal.svelte -->
<script lang="ts">
  import { Terminal } from 'xterm';
  import { FitAddon } from 'xterm-addon-fit';
  import { onMount, onDestroy } from 'svelte';

  export let containerId: string;

  let terminalEl: HTMLDivElement;
  let terminal: Terminal;
  let ws: WebSocket;

  onMount(() => {
    terminal = new Terminal();
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.open(terminalEl);
    fitAddon.fit();

    // Connect WebSocket
    ws = new WebSocket(`ws://${location.host}/api/terminal/${containerId}`);
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === 'output') {
        terminal.write(msg.data);
      }
    };

    // Handle input
    terminal.onData((data) => {
      ws.send(JSON.stringify({ type: 'input', data }));
    });
  });

  onDestroy(() => {
    ws?.close();
    terminal?.dispose();
  });
</script>

<div bind:this={terminalEl} class="terminal" data-testid="terminal"></div>
```

### Process Status Display
```svelte
<!-- Required for E2E testing -->
<div data-testid="process-status" class="status {status}">
  {status}
</div>
```

### API Client Pattern
```typescript
// client.ts
const API_BASE = '/api';

export async function getProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function createProject(data: CreateProject): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

### TypeScript Types
```typescript
// types/api.ts - Mirror backend Pydantic models
export interface Project {
  id: string;
  name: string;
  path: string;
  created_at: string;
  container_id?: string;
}

export interface Container {
  id: string;
  project_id: string;
  status: 'created' | 'running' | 'exited' | 'error';
}

export interface TerminalMessage {
  type: 'output' | 'status' | 'error';
  data?: string;
  state?: 'running' | 'exited' | 'error';
}

export interface TerminalCommand {
  type: 'input' | 'interrupt' | 'resize';
  data?: string;
  cols?: number;
  rows?: number;
}
```

## Beads Workflow

```bash
# Start of session
bd ready                              # Find available work
bd update <id> --status=in_progress   # Claim it

# During work
# ... implement ...

# After completing each issue
bd close <id>
bd sync

# End of session
git add .
git commit -m "Frontend: <description>"
git push -u origin frontend
bd sync
```

## Quality Gates

Before pushing:
```bash
# Type check
npm run check

# Unit tests
npm run test:unit

# Build check
npm run build

# E2E tests (if backend available)
npm run test:e2e
```

## Coordination Points

You will need to wait for or coordinate with other agents:

1. **Wait for backend contracts** - Need TypeScript types from Pydantic models
2. **Wait for WebSocket endpoint** - Need backend ready for terminal testing
3. **Wait for mock-claude** - Need Infrastructure to provide mock for E2E tests

Use beads comments for coordination:
```bash
bd comment <issue-id> "Waiting for backend WebSocket endpoint"
```

## PWA Requirements

### manifest.json
```json
{
  "name": "Claude Dev Container",
  "short_name": "Claude Dev",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a1a",
  "theme_color": "#6366f1",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### Service Worker Strategy
- Cache project list for offline viewing
- Show offline indicator when disconnected
- Commands require active connection

## Do NOT

- Create backend files
- Create Docker files
- Modify API contracts without coordination
- Push to main branch directly
- Parse terminal output in tests (use data-testid elements)
