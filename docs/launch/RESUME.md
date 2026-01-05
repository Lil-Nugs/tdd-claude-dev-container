# Resume Guide

Start each new session by reading this file. I'll figure out where you left off and continue.

## How to Resume

Just say:
```
read docs/launch/RESUME.md and continue
```

I'll check the beads tags and git state to determine the current phase, then pick up where we left off.

---

## State Detection

I check these to determine progress:

### Phase 0 Complete?
```bash
bd list --tag=contracts-frozen    # Need 1
bd list --tag=environment-ready   # Need 1
bd list --tag=fixtures-ready      # Need 1
```

### Phase 1 Complete?
```bash
git log origin/backend --oneline -1   # Has commits?
git log origin/frontend --oneline -1  # Has commits?
git log origin/infra --oneline -1     # Has commits?
```

### Phase 2 Complete?
```bash
bd list --tag=reviewed           # Need 3
bd list --priority=0 --status=open  # Need 0
bd list --priority=1 --status=open  # Need 0
```

### Phase 3 Complete?
```bash
bd list --tag=merge-complete         # Need 1
bd list --tag=integration-complete   # Need 1
```

### Phase 4 Complete?
```bash
bd list --tag=docs-complete    # Need 1
```

---

## Decision Tree

```
IF no contracts-frozen tag:
  → Run Phase 0

ELSE IF no commits on backend/frontend/infra branches:
  → Run Phase 1

ELSE IF less than 3 reviewed tags OR P0/P1 issues open:
  → Run Phase 2 (or fix issues first)

ELSE IF no merge-complete tag:
  → Run Phase 3

ELSE IF no docs-complete tag:
  → Run Phase 4

ELSE:
  → Done! Ready for release
```

---

## Quick Status Check

Run this to see current state:
```bash
echo "=== Phase 0 ===" && bd list --tag=contracts-frozen --tag=environment-ready --tag=fixtures-ready
echo "=== Phase 1 ===" && git branch -r | grep -E "backend|frontend|infra"
echo "=== Phase 2 ===" && bd list --tag=reviewed && bd list --priority=0 --priority=1 --status=open
echo "=== Phase 3 ===" && bd list --tag=merge-complete --tag=integration-complete
echo "=== Phase 4 ===" && bd list --tag=docs-complete
```
