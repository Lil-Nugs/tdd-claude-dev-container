# Launch Commands

Just tell me what to do:

## Quick Commands

| Say this | I'll do this |
|----------|--------------|
| `run phase 0` | Setup contracts, environment, fixtures |
| `run phase 1` | Spawn backend, frontend, infra agents (parallel) |
| `run phase 2` | Spawn review agents (parallel) |
| `run phase 3` | Merge branches and run E2E tests |
| `run phase 4` | Update documentation |
| `run all` | Execute all phases in sequence |

## Individual Agents

| Say this | I'll spawn |
|----------|-----------|
| `spawn contracts agent` | Creates shared types |
| `spawn environment agent` | Sets up worktrees |
| `spawn fixture agent` | Creates test infrastructure |
| `spawn backend agent` | Implements FastAPI backend |
| `spawn frontend agent` | Implements SvelteKit PWA |
| `spawn infra agent` | Implements Docker/CI/CD |
| `spawn watchdog` | Monitors progress |
| `spawn backend review` | Reviews backend code |
| `spawn frontend review` | Reviews frontend code |
| `spawn infra review` | Reviews infrastructure |
| `spawn merge agent` | Merges branches |
| `spawn integration review` | Runs E2E tests |
| `spawn docs agent` | Updates documentation |

## Status Commands

| Say this | I'll show |
|----------|-----------|
| `check status` | Current phase, agent status, beads stats |
| `check gates` | Whether ready for next phase |
| `show issues` | Open beads issues |

## Phase Details

Each phase has a launch file with exact prompts:
- `docs/launch/phase-0.md` - Setup
- `docs/launch/phase-1.md` - Implementation
- `docs/launch/phase-2.md` - Review
- `docs/launch/phase-3.md` - Integration
- `docs/launch/phase-4.md` - Documentation

Just say "read phase-1 and execute" and I'll do it.

---

## Workflow Overview

```
Phase 0: Setup
├── Contracts Agent ──────┐
├── Environment Agent ────┼──▶ Fixtures Agent
└──────────────────────────┘

Phase 1: Implementation (all parallel)
├── Backend Agent
├── Frontend Agent
├── Infra Agent
└── Watchdog Agent

Phase 2: Review (all parallel)
├── Backend Review
├── Frontend Review
└── Infra Review

Phase 3: Integration
├── Merge Agent ──▶ Integration Review

Phase 4: Sign-off
└── Documentation Agent ──▶ 🎉 Release
```

---

## Examples

**Start fresh:**
```
read docs/LAUNCH.md
run phase 0
```

**Continue after setup:**
```
read docs/launch/phase-1.md and spawn all implementation agents
```

**Check if ready for review:**
```
check gates for phase 2
```

**Fix an issue found in review:**
```
spawn a fix agent for beads-123
```

**Just run everything:**
```
read docs/LAUNCH.md and run all phases
```
