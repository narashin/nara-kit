---
name: pr
description: Generate a Pull Request title and body by auto-detecting base branch and analyzing commits. Writes in Korean. Triggers on "pr", "PR 만들어", "pull request", "PR 제목", "/pr".
version: 0.1.0
---

# pr — Smart PR Generator

Generate a Pull Request title and body by intelligently detecting the base branch. Write in Korean.

## Automatic Base Branch Detection

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

## Title Format
`<TICKET-ID> <primary-type>: <Subject>`
- Ticket ID: most frequent from commits (PROJ-###, etc.). None → `NO-ISSUE`
- Primary type priority: feat > fix > refactor > perf > chore > docs > test
- Subject: 60-72 chars, capitalized present verb

## Body Sections
- Overview (2-4 bullets, why + user impact)
- Changes (grouped by type)
- Breaking Changes
- Affected Areas / Risk
- Validation
- Rollout / Backout
- Linked Issues (`Closes TICKET-ID`)
