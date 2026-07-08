# Multi-Worktree / Multi-Branch Repos

Applies when the repo uses multiple `git worktree` checkouts (one per feature branch) and/or a shared
local integration branch that merges several PRs together for cross-PR testing before the real merge.

## Worktree Drift Check (Phase 3, before VERIFY)

Before implementing any ACCEPT/REBUT fix, diff the file as it exists on the **PR's own head-branch
worktree** against the review comment's `diff_hunk`. Do not assume the file in whatever checkout is
currently open matches what the PR actually shows on GitHub/GHE.

A shared local integration branch can silently carry a *different* version of the same file path -- two
PRs independently touch the same file, and whichever merged into the integration branch last wins,
overwriting the other PR's version there. Fixing the integration branch's copy in that case does
nothing for the actual open PR; the review thread would stay substantively unresolved even after
posting a reply claiming otherwise.

```bash
# Locate the PR's own head-branch worktree
git worktree list
# Confirm the file matches the comment's diff_hunk before editing
git -C <pr-head-worktree-path> show <commit_id>:<path> | diff - <(cat <<'EOF'
<diff_hunk content from the review comment>
EOF
)
```

If the integration branch's version differs structurally, apply the same *intent* (not a blind copy of
the diff) to each branch's actual code, and verify tests pass in both locations independently.

## Dual-Branch Commit + Push + Verify (Phase 7)

When a fix must land on both the PR's own branch and a local integration branch:

1. Commit and push the PR's own head branch first -- that is what the live PR/review actually reflects.
2. Separately commit an adapted version to the integration branch. Do not assume the diff applies
   cleanly; the branch may have diverged (see drift check above).
3. After every push, verify it actually landed -- a clean-looking command is not proof:
   ```bash
   git rev-parse HEAD
   git ls-remote origin refs/heads/<branch>
   ```
   The two SHAs must match. A `git push` can be silently cut short by a command-execution timeout while
   a slow pre-push hook (e.g. a full test suite) is still running, with no explicit failure message --
   the commit succeeded locally but origin never advanced. Re-run `git push` with a longer timeout and
   re-verify via `ls-remote` if there's any doubt.
