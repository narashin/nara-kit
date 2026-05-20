---
name: wt
description: >-
  Create a git worktree for a Jira ticket. Fetches the ticket summary, generates a kebab-case slug,
  asks the user for a git type prefix (never auto-mapped from Jira issue type), and invokes the shell
  `wt` helper to create the worktree at `../{repo}-{ticket}-{slug}`.
  USE FOR: "wt", "/wt TICKET-ID", "worktree 만들어", "워크트리 생성", "create worktree from ticket".
  DO NOT USE FOR: switching worktrees (use `cd`), removing worktrees (use `git worktree remove`),
  creating branches without a ticket (use plain `wt <branch>` in shell), or PR creation (use `/pr`).
---

# wt — Worktree from Jira Ticket

Bridges Jira ticket → branch name → shell `wt` helper, producing a worktree with the canonical
`{repo}-{ticket}-{slug}` directory layout.

## Arguments

`<ticket-id> [type-prefix]`

- `<ticket-id>` (required): Jira key, e.g. `LYRIS-346`.
- `[type-prefix]` (optional): git branch type. Allowed: `feature`, `fix`, `hotfix`, `chore`, `release`, `test`, or `none`. If omitted, the skill asks via `AskUserQuestion`. **Never auto-derive from Jira issue type.**

## Steps

1. **Parse args** into `TICKET` and optional `TYPE`.
2. **Verify git repo**: run `git rev-parse --show-toplevel`. If it fails, abort and ask the user to `cd` into the repo first.
3. **Fetch ticket** via `mcp__jira__jira_get_issue` with `issue_key=<TICKET>`, `fields=summary,status,issuetype`.
4. **Generate slug** from the summary:
   - lowercase kebab-case
   - 2–4 words max
   - drop articles (a/an/the), filler (just/really/basically), prepositions when removable without losing meaning
   - preserve technical terms (API names, acronyms) verbatim
   - example: `"Edit Planned Date After Approval"` → `edit-planned-date`
   - if summary is empty / TBD / single ambiguous word → present 2–3 slug candidates and ask the user to pick, **do not guess**.
5. **Resolve type prefix**:
   - If `TYPE` provided as 2nd arg → use it as-is.
   - If omitted → `AskUserQuestion` with options: `feature`, `fix`, `hotfix`, `chore`, `release`, `test`, `none (no prefix)`.
6. **Compose branch name**:
   - With prefix: `<TYPE>/<TICKET>-<slug>` (e.g. `feature/LYRIS-346-edit-planned-date`)
   - With `none`: `<TICKET>-<slug>` (e.g. `LYRIS-346-edit-planned-date`)
7. **Show plan** as a single line: `branch: <branch>  →  dir: ../<repo>-<TICKET>-<slug>`. Wait for explicit confirm (`ok`/`yes`/`go`). If the user proposes a different slug, regenerate and re-confirm.
8. **Execute via Bash**:
   ```bash
   wt <branch>
   ```
   The shell `wt` helper (defined in `~/.zshrc`) creates the worktree, strips the type prefix when forming the directory name, and `cd`s into it. **Do not call `git worktree add` directly** — always go through `wt`.
9. **Report** the resulting worktree path (`pwd`) and current branch (`git branch --show-current`).

## Constraints

- **No Jira-issue-type → git-prefix mapping.** Issue type (Story/Bug/Task/Sub-task) is not a reliable signal for branch type in this team. Always defer prefix choice to the user.
- **If the branch already exists**, `wt` reuses it. State this in the report.
- **Auto mode**: even in auto mode, the slug confirm and prefix selection steps are mandatory — naming is a decision the user must own. Skip confirm only if the user explicitly opts out for this session.
- **Never call `EnterWorktree` (superpowers native tool)** — places worktree under `.claude/worktrees/`, which violates the `{repo}-{ticket}-{slug}` sibling convention.

## Examples

User: `/wt LYRIS-346 feature`
- Summary: "Edit Planned Date After Approval"
- Slug: `edit-planned-date`
- Plan: `branch: feature/LYRIS-346-edit-planned-date  →  dir: ../iris-ui-LYRIS-346-edit-planned-date`
- Confirm → `wt feature/LYRIS-346-edit-planned-date` → ready at `../iris-ui-LYRIS-346-edit-planned-date`

User: `/wt LYRIS-432 fix`
- Summary: "Pin pnpm version to prevent Docker build failure"
- Slug: `pin-pnpm-version`
- Plan: `branch: fix/LYRIS-432-pin-pnpm-version  →  dir: ../iris-ui-LYRIS-432-pin-pnpm-version`

User: `/wt LYRIS-346`
- Summary: "Edit Planned Date After Approval"
- Skill asks: pick prefix (feature/fix/hotfix/chore/release/test/none).
- User picks `feature` → continues as above.

User: `/wt LYRIS-999 feature`
- Summary: "TBD"
- Skill asks user for a manual slug — does not guess.
