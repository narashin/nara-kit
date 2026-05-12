# PR Respond Execution Procedure

## Phase 1: Collection

1. **PR info fetch**:
   ```bash
   gh pr view [number] --json number,url,headRefName,baseRefName,author
   gh repo view --json owner,name
   ```

2. **Review comments fetch** (concurrency: 3):
   ```bash
   # Inline review comments
   GH_HOST={hostname} gh api repos/{owner}/{repo}/pulls/{number}/comments
   # PR-level reviews (approve/request_changes/comment + body)
   GH_HOST={hostname} gh api repos/{owner}/{repo}/pulls/{number}/reviews
   # Issue comments (general comments)
   GH_HOST={hostname} gh api repos/{owner}/{repo}/issues/{number}/comments
   ```
   **GHE**: Use `GH_HOST={hostname}` env var. No `--hostname` flag.

3. **Bot filtering**: Ignore `code-aimigo[bot]`, `github-actions[bot]`, `snyk[bot]`, `dependabot[bot]`, etc. (`user.type === "Bot"` or login contains `[bot]`)

4. **Unreplied only**: Filter to root comments without own reply.
   `--status` mode: output list and exit here.

## Phase 2: Classification

| Category | Description | Action |
|----------|-------------|--------|
| `blocking` | Security, bug, critical | Must verify -> accept or rebut |
| `suggestion` | Code improvement | Verify -> judge |
| `question` | Intent/design question | Explain reply |
| `nitpick` | Style, naming, format | Quick accept or explain |
| `praise` | Positive feedback | Skip (no reply needed) |

## Phase 3: Evaluation (per comment)

**READ -> UNDERSTAND -> VERIFY -> EVALUATE -> RESPOND**:

1. **UNDERSTAND**: Grasp reviewer intent
   - Unclear -> write question reply first (do not implement)
   - Multiple related comments -> holistic judgment (no partial accepts)

2. **VERIFY**: Confirm in codebase
   - Read file:line
   - Check if reviewer's issue is real
   - Check related tests
   - Check implementation history (git blame)

3. **EVALUATE**: Technical judgment
   - Technically correct for this codebase?
   - Breaks existing functionality?
   - Intentional reason for current implementation?
   - YAGNI? (grep for actual usage)

## Phase 4: Decision

```
IF reviewer technically correct:
  -> ACCEPT (Phase 5)

IF reviewer lacks context or technically inaccurate:
  -> REBUT (Phase 6)

IF uncertain or architecture decision needed:
  -> HOLD -- delegate to user (present analysis only)
```

## Phase 5: Accept Path

### 5-1. Impact Analysis
- Trace callers of changed function/type (Grep -- direct calls, type refs, re-exports, dynamic imports)
- Check related test files
- API contract changes?

### 5-2. Design Consideration
- Is the proposed approach optimal? Better alternatives?
- Consistent with existing codebase patterns?
- Implement as-suggested vs. intent-preserving alternative -- reasoned choice

### 5-3. Implementation
- Apply changes one at a time (no batch)
- `npx tsc --noEmit` (or project type-check)
- Run related tests
- Confirm no regressions

### 5-4. Reply
Inline reply via `gh api repos/{owner}/{repo}/pulls/{number}/comments/{id}/replies -f body="..."`:

```
Fixed. [one-line description of change]
```

Alternative implementation:
```
Fixed differently -- [alternative + reason]. [change description]
```

## Phase 6: Rebut Path

Rebut reasons (one or more):
- Breaks existing functionality
- Reviewer lacks full context
- YAGNI (grep shows no usage)
- Technically inaccurate for this stack
- Legacy/compatibility reason exists
- Conflicts with user's architecture decision

Reply format:
```
[Current implementation reason]. [Technical evidence -- code/test reference].
[Question or alternative (if applicable)]
```

## Phase 7: Wrap-up

1. **Changes summary** (when accepts exist):
   - Changed file list + diff summary
   - **Commit message suggestion** -- format: `fix: <one-line>`. No auto-commit.
   - Confirm push with user

2. **Summary output**
