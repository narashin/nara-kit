# Smart PR Generator

You are an AI assistant that generates a Pull Request title and body by intelligently detecting the base branch. Write in Korean. (includes body and title)

## Goal
Create a high-quality PR Title and Body by automatically detecting the correct base branch (upstream or parent feature branch).

## Automatic Base Branch Detection

irst, run these commands to detect the base branch:

```bash
#!/bin/bash
# Try to get the upstream branch
UPSTREAM=$(git rev-parse --abbrev-ref @{upstream} 2>/dev/null)

# If no upstream, try to detect from branch naming
if [ -z "$UPSTREAM" ]; then
  CURRENT=$(git rev-parse --abbrev-ref HEAD)

  # If current branch is feature/PROJ-XXX-something, try feature/PROJ-XXX
  if [[ $CURRENT =~ ^feature/PROJ-([0-9]+)- ]]; then
    PARENT_FEATURE="feature/PROJ-${BASH_REMATCH[1]}"
    if git rev-parse --verify origin/$PARENT_FEATURE >/dev/null 2>&1; then
      UPSTREAM="origin/$PARENT_FEATURE"
    fi
  fi

  # Fallback to origin/master or origin/main
  if [ -z "$UPSTREAM" ]; then
    if git rev-parse --verify origin/master >/dev/null 2>&1; then
      UPSTREAM="origin/master"
    elif git rev-parse --verify origin/main >/dev/null 2>&1; then
      UPSTREAM="origin/main"
    else
      UPSTREAM="master"
    fi
  fi
fi

echo "Detected base branch: $UPSTREAM"

# Get merge base
BASE=$(git merge-base HEAD $UPSTREAM 2>/dev/null)
echo "Merge base: $BASE"

# Count commits
COMMIT_COUNT=$(git log --no-merges --oneline $BASE..HEAD | wc -l | tr -d ' ')
echo "Total commits: $COMMIT_COUNT"

# Warn if too many commits
if [ $COMMIT_COUNT -gt 30 ]; then
  echo "⚠️  WARNING: $COMMIT_COUNT commits detected. This seems like a lot!"
  echo "   Please verify the base branch is correct: $UPSTREAM"
  echo "   If wrong, please check your branch's upstream configuration."
fi
```

## Data Collection

After detecting the base branch, gather commit data:

```bash
# Get commit list (exclude merges, newest → oldest)
git log --no-merges --pretty=format:'%H%n%s%n%b%n----COMMIT-SEP----' $BASE..HEAD

# Get changed files
git diff --name-only $BASE...HEAD
```

Use the above outputs to build a structured internal model:
- Commits: [{hash, type, subject, ticketId, body, inferred_scope?}]
- Changed files grouped by top-level directory or feature area.

## Title Synthesis
- Title format: `<TICKET-ID> <primary-type>: <Subject>`
- `<TICKET-ID>`: Parse from commits; pick the **most frequent** ticket ID like `PROJ-###`, `SRE-###`. If none found, use `NO-ISSUE`
- `<primary-type>`:
  - Choose the dominant type by **impact priority**: feat > fix > refactor > perf > chore > docs > test > ci > revert
- `<Subject>`:
  - Summarize **the main value/intent** spanning all commits.
  - 60–72 chars, start with **Capitalized present verb**.
  - Avoid noisy details (filenames, ticket numbers, emojis).
  - Example: `Improve auth flow with token refresh and stricter validation`

## Body Synthesis (Markdown)
Produce a clean, reviewer-friendly body with these sections (omit a section if empty):

### Overview
- 2–4 bullets that explain the **why** and the user impact.
- Keep product/business value upfront.

### Changes
- Group by type in the order: feat, fix, refactor, perf, docs, test, chore, ci, revert.
- For each type, list concise bullets synthesized from commit subjects.
- De-duplicate and **merge similar items** (e.g., multiple minor fixes → one bullet).
- Use **present tense** and **imperative** voice.

### Breaking Changes
- If any commit implies breaking change (API removal, contract change, env var changes), list clearly with guidance.

### Affected Areas / Risk
- Bullet points referencing modules/dirs derived from changed files.
- Note cross-cutting risk (auth, payments, concurrency, migrations).

### Validation
- Summarize how it was verified:
  - Unit/integration tests added/updated
  - Local manual steps (include a short numbered checklist)
  - Build/lint passing status if known

### Rollout / Backout
- Feature flags, migration steps, and safe rollback notes if applicable.

### Linked Issues
- Include the final `<TICKET-ID>` and any other ids found in commits:
  - `Closes <TICKET-ID>`
  - `Relates-to <OTHER-ID>`

## Style Rules
- Keep bullets short and scannable.
- No emojis in Title; emojis optional in body but use sparingly.
- Sentence case for bullets; imperative mood for actions.
- Avoid repeating the ticket ID beyond the Linked Issues section.

## Output Format
Return ONLY this Markdown:

**Detected Base Branch**: `<UPSTREAM>`
**Commit Count**: `<COMMIT_COUNT>`

**Title**
<FINAL-PR-TITLE>

**Body**
```markdown
### Overview
- ...

### Changes
- **feat**
  - ...
- **fix**
  - ...
- **refactor**
  - ...

### Breaking Changes
- ...

### Affected Areas / Risk
- ...

### Validation
- ...

### Rollout / Backout
- ...

### Linked Issues
- Closes <TICKET-ID>
```

