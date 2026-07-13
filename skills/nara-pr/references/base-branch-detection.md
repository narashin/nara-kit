# Base Branch Detection Script

```bash
UPSTREAM=$(git rev-parse --abbrev-ref @{upstream} 2>/dev/null)
if [ -z "$UPSTREAM" ]; then
  CURRENT=$(git rev-parse --abbrev-ref HEAD)
  if [[ $CURRENT =~ ^feature/PROJ-([0-9]+)- ]]; then
    PARENT_FEATURE="feature/PROJ-${BASH_REMATCH[1]}"
    if git rev-parse --verify origin/$PARENT_FEATURE >/dev/null 2>&1; then
      UPSTREAM="origin/$PARENT_FEATURE"
    fi
  fi
  if [ -z "$UPSTREAM" ]; then
    if git rev-parse --verify origin/master >/dev/null 2>&1; then
      UPSTREAM="origin/master"
    else
      UPSTREAM="origin/main"
    fi
  fi
fi
BASE=$(git merge-base HEAD $UPSTREAM 2>/dev/null)
```

## Priority order

1. Tracked upstream branch (`@{upstream}`)
2. Parent feature branch (`feature/PROJ-{N}` from `feature/PROJ-{N}-sub`)
3. `origin/master`
4. `origin/main` (fallback)
