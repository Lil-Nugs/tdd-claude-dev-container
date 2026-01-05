# Session-Based Workflow

Each phase runs in its own Claude session to avoid context limits.

---

## Session 1: Phase 0 (Setup)

**Start a new Claude session and say:**
```
read docs/launch/phase-0.md and execute it
```

**When done, verify:**
```bash
bd list --tag=contracts-frozen
bd list --tag=environment-ready
bd list --tag=fixtures-ready
```

**End session.**

---

## Session 2: Phase 1 (Implementation)

**Start a new Claude session and say:**
```
read docs/launch/phase-1.md and spawn all implementation agents in parallel
```

**Monitor progress:**
```
/tasks
bd stats
```

**When all agents complete, verify:**
```bash
git fetch --all
git log origin/backend --oneline -1
git log origin/frontend --oneline -1
git log origin/infra --oneline -1
```

**End session.**

---

## Session 3: Phase 2 (Review)

**Start a new Claude session and say:**
```
read docs/launch/phase-2.md and spawn all review agents in parallel
```

**When done, verify:**
```bash
bd list --tag=reviewed  # Should show 3
bd list --priority=0 --status=open  # Must be 0
bd list --priority=1 --status=open  # Must be 0
```

**If P0/P1 issues exist:**
```
fix the P0 and P1 issues
```
Then end session and start a new one to re-review.

**End session.**

---

## Session 4: Phase 3 (Integration)

**Start a new Claude session and say:**
```
read docs/launch/phase-3.md and execute it
```

**When done, verify:**
```bash
bd list --tag=merge-complete
bd list --tag=integration-complete
git log main --oneline -5  # Should show merges
```

**End session.**

---

## Session 5: Phase 4 (Documentation)

**Start a new Claude session and say:**
```
read docs/launch/phase-4.md and execute it
```

**When done, verify:**
```bash
bd list --tag=docs-complete
```

**Tag release:**
```
tag this as v1.0.0 and push
```

**Done!**

---

## If You Lose Track

Start any session with:
```
read docs/launch/RESUME.md and continue
```

I'll figure out where you are and what to do next.
