# Stacked publication: one branch, several PRs

Read this only when SKILL.md Step 2 sees several review concerns, or the user asked to split the branch. A single PR never reads it.

The branch is already implemented and verified. Splitting rebuilds that exact result as a chain of new branches; it never edits, adds, or drops product content.

## 1. Single or stacked

Decide by review concern, not size. There is no line-count threshold.

- `stacked` when the branch holds two or more concerns that a reviewer can read separately and that form one **linear** dependency (for example model and migration, then domain rule and its tests, then endpoint and screen). Different reviewer audiences are a strong signal.
- `single` when there is one concern, however large. Generated files, lockfiles, snapshots, vendored code, and renames follow their owning concern; they never create a layer by themselves.
- The concerns are unrelated (two features on one branch) → stop. Say which paths belong to which feature and suggest separate branches. One run publishes one story.
- The dependency is not linear → use fewer layers, or `single`.
- A PR already exists for this head → `single` (existing-PR mode). Never restructure a PR that is under review.

## 2. Plan the layers

Record the source first and keep it as the recovery point:

```bash
SOURCE_BRANCH=$(git rev-parse --abbrev-ref HEAD)
ORIGINAL_HEAD=$(git rev-parse HEAD)
ORIGINAL_TREE=$(git rev-parse "$ORIGINAL_HEAD^{tree}")
BASE_ANCHOR=$(git merge-base "$ORIGINAL_HEAD" "origin/$BASE")
```

Read the whole `BASE_ANCHOR...ORIGINAL_HEAD` diff and assign **every changed path to exactly one layer** by what it serves, not by which commit touched it. Commit boundaries are reused only when they already match the layers in dependency order.

- A file that mixes two concerns goes to the lower layer that needs it, or the two layers merge. Never split hunks to reach a target size.
- A layer that cannot build or pass its own smallest check without a path from a higher layer merges with its neighbour.
- Branch names: `<source branch>-<n>-<concern>` unless the repository has its own convention. Check they do not exist locally or on the remote.

Each layer gets its own title (repo-rules.md applies to every layer) and a body that explains only that layer, plus one line on what it builds on. Do not copy the whole feature summary into every PR. The QA table goes on the layer whose behavior it checks.

## 3. Tool: gh-stack or a plain chain

Decide with read-only checks, before the confirm screen:

1. `gh extension list` shows an extension from exactly `github/gh-stack` (not another `stack`).
2. `gh api --hostname <host> repos/<owner>/<repo>/stacks?per_page=1` answers 200. A 404 means the host has no Stack support (GitHub Enterprise Server 3.19 answers 404).

Both pass → gh-stack links the PRs into a Stack. Otherwise → a **plain PR chain**: each PR's base is the layer below it. Say so on the confirm screen, because after the bottom layer merges, the next PR's base must be moved by hand (`gh pr edit <n> --base <base>`). Never install or upgrade an extension. Never change the user's git config (no `rerere`).

## 4. Confirm screen

Nothing is created before approval: no branch, no commit, no push. Show:

```
형태: stacked (3층, PR 사슬: 이 호스트는 Stack API가 없어 base만 아래층으로 건다)
1. feature/PROJ-12-pay-1-schema ← main
   커밋: PROJ-12 feat: Add payment method column
   경로: src/models.py, migrations/004_pay_method.sql
   제목: PROJ-12 feat: Add payment method column
2. feature/PROJ-12-pay-2-rule ← feature/PROJ-12-pay-1-schema
   ...
불변식: 최상층 tree == 원래 tree (<ORIGINAL_TREE short>), push 전에 확인
원래 브랜치: <SOURCE_BRANCH> @ <short SHA> 그대로 둔다
층별 검사: <each layer's smallest check, or "없음: 저장소에 테스트 명령 없음">
```

With gh-stack the first line reads `형태: stacked (3층, gh-stack Stack)`. Below it, each layer's body preview the way SKILL.md Step 7 shows a single PR.

**One approval covers every listed layer commit, the pushes, and the PRs.** This is the exception to "one approval, one commit": the screen lists each commit subject, so the user approves them by name. Anything not on the screen (an extra layer, a fix-up commit, a rebase) needs a new approval.

## 5. After approval

Recheck that `HEAD`, the base tip, and the branch names have not moved. Any drift voids the approval: show the new plan.

Build from `BASE_ANCHOR`, not from a newer base tip, so the verified tree is reproduced exactly:

```bash
git switch -c <layer-1> "$BASE_ANCHOR"
git restore --source "$ORIGINAL_HEAD" --staged --worktree -- <layer-1 paths>
git diff --cached --name-status      # only layer-1 paths; anything else → stop
git commit -m "<approved subject>"
# run layer-1's smallest check
git switch -c <layer-2>               # from layer-1, same steps
```

Deleted and renamed paths go through the same `restore`. Never `git add -A` to cover an unclear layer.

Before any push, prove the chain is lossless. Both must pass, or stop as `Blocked` with the source branch untouched:

```bash
test "$(git rev-parse "<top layer>^{tree}")" = "$ORIGINAL_TREE"
git diff --exit-code "$ORIGINAL_HEAD" "<top layer>" --
```

Then publish bottom to top:

- Plain chain: push each layer, `gh pr create --base <layer below> --head <layer>` with the approved title and body.
- gh-stack: check `gh stack <command> --help` for current flags, `gh stack init <layer-1> <layer-2> ...`, `gh stack view --json` to confirm the chain, then `gh stack submit --auto --open` (draft: without `--open`). Submit derives titles from commits, so edit each PR to the approved title and body afterwards.

Push and PR creation are not atomic. If something fails halfway, reread the remote PRs and report exactly what exists. Do not retry through another route, close, or delete anything, and do not claim a rollback.

Never rebase, rename, force-push, or delete the source branch. Never merge the chain.

## 6. Receipt

Bottom-to-top PR URLs, the tree check result, the source branch and SHA kept, and for a plain chain the base-move reminder as the next action.

Provenance: adapted from tiger-kit `tk-pr-open` `references/split-to-stack.md` (MTGVim/tiger-kit `b483cdf`, MIT): concern-based split, source preservation, merge-base rebuild by path ownership, tree invariant, per-layer bodies. Changed: a disclosed plain PR chain when the host has no Stack API (tiger-kit stops), one approval for all listed layer commits. Omitted: approval packet file, evidence manifest, `rerere` config.
