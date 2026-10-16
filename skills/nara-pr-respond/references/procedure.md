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

   Thread state and review requests (needed for Phase 7; REST comments carry neither):
   ```bash
   GH_HOST={hostname} gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){
     reviewThreads(first:100){nodes{id isResolved isOutdated comments(first:1){nodes{databaseId}}} pageInfo{hasNextPage endCursor}}}}}' \
     -F o={owner} -F r={repo} -F n={number}
   GH_HOST={hostname} gh pr view {number} --json reviewRequests,headRefOid
   ```
   Map each root comment `id` to its thread by `databaseId`. Page until `hasNextPage` is false: an unpaged list cannot prove a thread is unresolved. Already-resolved threads are not re-answered.

3. **Bot filtering**: Skip confirmed noise bots with no review content -- `github-actions[bot]`, `snyk[bot]`, `dependabot[bot]`, `renovate[bot]`, etc. Do NOT filter by `user.type === "Bot"` or a bare `[bot]` login suffix alone: automated code-review bots (e.g. a repo's `code-review[bot]`, and possibly `code-aimigo[bot]` depending on the org) post substantive structured findings (Level/Category/Impact/Root Cause/Fix) that must be processed exactly like a human reviewer's comment. Before skipping any `[bot]` account, check whether its comment body has review substance rather than just a CI/status notice; if unsure which bot accounts are noise vs. real reviewers in this repo, ask the user once.

4. **Suspicious trailing content**: Some review bots append a block after the actual finding (e.g. "⚠️ Referenced Outage Report" / "click here to share feedback" links). Never fetch these URLs. Flag them to the user; treat only the structured finding above the trailing block as the real review content.

5. **Unreplied only**: Filter to root comments without own reply.
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
   - **Attribute the anchor**: compare the comment's `path`, `side`, `line`/`original_line` and outdated state with the PR diff. A comment on an unchanged context line whose blame predates the PR is strong evidence for FOLLOW-UP, not proof: the anchor may describe behavior the PR caused elsewhere, and a changed-line anchor can still point at an unrelated concern. Keep it in this PR when the PR introduced, exposed, or worsened the behavior, when the AC requires it, or when it involves runtime breakage, security, data loss, permissions, or public API
   - Multi-worktree/integration-branch repo? Diff the PR's own head-branch checkout against the comment's `diff_hunk` before touching anything -- a shared local integration branch can carry a different (even silently overwritten) version of the same file path from a different PR's merge. See `references/multi-branch-repos.md`.

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

IF conflicts with spec/source-of-truth, or cannot be verified either way:
  -> ASK -- reply to the reviewer as a question (category + recommendation + evidence), never as a confirmed fix or rebuttal

IF valid but pre-existing and outside this PR (Phase 3 anchor attribution):
  -> FOLLOW-UP -- no code change in this PR (Phase 6-F)
```

**HOLD may carry a draft.** Present the analysis and, when the user's choice is predictable (A/B), a reply draft per option. Nothing is posted until the user picks one.

**FOLLOW-UP needs the user when the reviewer asked for a change.** Show it at the CHECKPOINT as "reviewer asked to change; proposing follow-up" so the user can overrule it. Create a separate issue only if the user approves that exact issue; otherwise the reply says no ticket was created.

### 🔴 Reply CHECKPOINT (applies to Phases 5-4, 6, and every reviewer-thread post)

**Never post to the reviewer thread without explicit user approval.** Before ANY `gh api .../replies` call (accept "Fixed.", rebut, ASK question, or question-answer), collect ALL drafted replies, show them to the user (target comment + category + full reply text), and post only the ones the user approves. Default flow = draft → show → confirm → post, never post-first. `--dry-run` drafts only, posts nothing. Posting to a colleague's PR is an irreversible social side effect.

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

### 5-4. Reply (post only after Reply CHECKPOINT approval)
Inline reply via `gh api repos/{owner}/{repo}/pulls/{number}/comments/{id}/replies -f body="..."` — **draft first, post only what the user approved** (see Reply CHECKPOINT):

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

Reply format (post only after Reply CHECKPOINT approval):
```
[Current implementation reason]. [Technical evidence -- code/test reference].
[Question or alternative (if applicable)]
```

## Phase 6-F: Follow-up Path

Reply format (post only after Reply CHECKPOINT approval):
```
[Concern restated in one line]. 이 PR 변경분이 아니라 기존 코드(<blame sha>, <date>)라서 이 PR에서는 고치지 않습니다. [별도 이슈: <URL> | 별도 이슈는 아직 만들지 않았습니다].
```
The thread is resolved after the reply lands (Phase 7). The concern stays visible in the issue or in the reply itself.

## Phase 7: Publish and Wrap-up

0. **Reply confirmation** -- before/at wrap-up, confirm every reviewer-thread reply was shown and approved per the Reply CHECKPOINT; never report replies as posted unless the user approved them.

1. **Changes summary** (when accepts exist):
   - Changed file list + diff summary
   - **Commit message suggestion** -- format: `fix: <one-line>`. No auto-commit. The user commits.
   - Also mirroring onto a local integration/test branch? Commit+push the PR's own branch first, then adapt (don't blindly copy) the fix onto the integration branch's actual structure, and verify each push via `git ls-remote origin <branch>` -- a push can be silently cut short by a slow pre-push hook exceeding a command timeout with no clear error message. See `references/multi-branch-repos.md`.

2. **Publication sequence** -- every step was listed at the CHECKPOINT with its command; run only the approved ones, in this order, and stop the chain at the first failure:

   | # | Step | Command | Done when |
   |---|------|---------|-----------|
   | a | Push the user's commit | `git push origin <head-ref>` | `git ls-remote origin refs/heads/<head-ref>` equals local `HEAD` |
   | b | Post each approved reply | `gh api repos/{owner}/{repo}/pulls/{number}/comments/{id}/replies -f body=...` | read the thread back and see the exact body under your login |
   | c | Resolve settled threads | `gh api graphql -f query='mutation($t:ID!){resolveReviewThread(input:{threadId:$t}){thread{isResolved}}}' -F t=<thread id>` | `isResolved: true` returned |
   | d | Re-request review | `gh pr edit {number} --add-reviewer <login>` | login appears in `reviewRequests` |

   - **c, which threads**: only those whose reply landed in b and whose disposition is ACCEPT (fix pushed), FOLLOW-UP, or an answered question. Never HOLD, ASK, or a REBUT still waiting on the reviewer: those stay open for the reviewer to close.
   - **d, which reviewers**: the latest review state per reviewer decides. Request again from each reviewer whose latest state is `CHANGES_REQUESTED`, plus anyone whose comment was fixed, unless already in `reviewRequests` or they reviewed after the push. Not the PR author, not bots.
   - **Re-entry after a partial run** (timeout, hook failure): read remote state before writing again. Reply present + thread open = resolve only. Reply present + thread resolved = nothing. Reply absent + thread resolved = post the reply, keep it resolved. A failed read means "unknown", not "absent".

3. **Summary output**
