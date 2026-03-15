# Safe Merge Plan: main + niki

## Current State (as of check)

| Branch | HEAD | Status |
|--------|------|--------|
| **main** | `0ced9bc` | Merge main into niki: keep niki frontend, adopt main backend |
| **niki** | `ea815ba` | Frontend fix (1 commit ahead of main) |

- **Merge base:** `0ced9bc` (main and niki share this)
- **niki** has 1 extra commit: `ea815ba` (Frontend fix) — Mapbox integration, events API, attribution hide, etc.

## Strategy: "Take all of main, merge niki safely"

Since main is the base and niki adds 1 commit on top, the merge is straightforward.

### Step 1: Ensure clean state
```bash
git status   # must be clean
git fetch origin
```

### Step 2: Merge niki into main
```bash
git checkout main
git pull origin main
git merge niki -m "Merge niki: Frontend fix (Mapbox events, attribution, useEventsNearby)"
```

- **Expected:** Fast-forward or clean merge (no conflicts, since main hasn’t diverged)
- **If conflicts:** Resolve in favor of **main** (keep main’s version)

### Step 3: Push main
```bash
git push origin main
```

### Step 4: Sync niki with main
```bash
git checkout niki
git merge main -m "Sync niki with main"
git push origin niki
```

### Step 5: Verify
```bash
git log --oneline -3 main
git log --oneline -3 niki
# Both should show same latest commit
```

---

## Rollback (if needed)

```bash
git checkout main
git reset --hard origin/main   # before push
# or
git revert -m 1 <merge_commit> # after push
```

---

## Summary

- **main** gets niki’s Frontend fix commit.
- **niki** and **main** end up at the same commit.
- No conflicts expected; if any, prefer main’s version.
