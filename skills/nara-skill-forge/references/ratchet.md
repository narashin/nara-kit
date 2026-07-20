# Working-Tree Regression Ratchet

nara-kit skills never auto-commit (the user commits manually), so the ratchet
operates on the **uncommitted working tree**, not git history.

## Mechanic

Per fix in Phase 4:

1. **Snapshot** — before editing, copy the current SKILL.md to
   `SKILL.md.forge-bak` (or `git stash` the working tree if it is otherwise clean).
2. **Apply** one-theme fix.
3. **Re-grade** — rerun Phase 2-3 with a FRESH subagent. Never grade in the same
   context that wrote the fix (optimism bias inflates the score).
4. **Decide**:
   - **Kept** — new grades ≥ old on every previously-passing grader AND
     new-unclear ≤ old AND token budget not regressed → delete the snapshot,
     advance the baseline.
   - **Restored** — any prior-passing grader now fails, OR unclear count rose, OR
     token budget grew → restore the snapshot over SKILL.md, log the failed
     attempt, move to the next-lowest theme (do not blindly retry the same one).

## Rules

- Improvement must be **strict** on the targeted dimension and **non-regressing**
  on all others.
- One theme per fix so a regression is attributable to a single change.
- Diminishing returns — 2 consecutive kept-fixes with delta below one grader →
  stop (Phase 5 cutoff). Do not pad the body to look "more detailed".

## Exception table

| Situation | Trigger | Action |
|---|---|---|
| Not a git repo | `git rev-parse` fails | use file snapshot `SKILL.md.forge-bak`, not stash |
| Snapshot exists | `.forge-bak` left by a crashed run | ask user: reuse / discard / diff first |
| Re-grade unavailable | subagent timeout / resource limit | mark iteration `dry_run`; do NOT keep a fix on dry-grade alone; flag it in the presentation |
| Token budget regressed | new SKILL.md tokens > old | restore even if graders pass — bloat is a regression |
| Restore fails | file lock / partial write | re-read `.forge-bak`, overwrite SKILL.md manually, warn user |

Surface every exception to the user before acting — never silently keep or drop a fix.
