# Quick Start

Just tell me which phase to run:

| Command | What it does |
|---------|--------------|
| `run phase 0` | Setup: Contracts + Environment + Fixtures |
| `run phase 1` | Implementation: Backend + Frontend + Infra (parallel) |
| `run phase 2` | Review: All three domain reviews (parallel) |
| `run phase 3` | Integration: Merge + E2E testing |
| `run phase 4` | Documentation: Final docs update |
| `run all` | Run everything in sequence |

Or be specific:
- `spawn backend agent`
- `spawn review agents`
- `spawn watchdog`

I'll read the appropriate launch file and execute it.
