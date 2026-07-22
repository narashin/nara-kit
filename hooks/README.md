# nara-kit hooks

## review-gate (PreToolUse → `nara-review-gate.py`)

Deterministic enforcement of the dev-mode `code-review` spine step. Blocks a
`git commit` that stages **source** changes when no fresh code-review artifact
exists under `docs/review/`.

### Why

Prose instructions ("don't skip the review gate") are weak against
completion-momentum bias — the agent rationalizes the gate away under "small
scope" and commits unreviewed source. This hook is model-independent: the commit
simply cannot proceed, so the bias has nothing to act on.

### When it fires

All of these must hold, else it silently allows:

1. The Bash command invokes `git commit` at a command position (start, or after
   `;` `&&` `||` `|` `then` `do`) — mentions inside `echo`/`grep`/quotes are ignored.
2. The repo is in an active nara dev-mode session — `docs/gap.md` or
   `docs/plan.md` exists at the repo root.
3. The staged set touches non-doc, non-test **source** (excludes `*.md`,
   `docs/`, `.claude/`, `tests/`, `*.test.*`, `*.spec.*`).

Then it blocks if `docs/review/` has **no** report, or the newest report is
**older** than the newest staged source file (stale review).

### Escape hatches (for genuine trivia)

- Add `[skip-review]` anywhere in the commit message.
- Export `NARA_SKIP_REVIEW=1`.

Fails **open** on any unexpected error — a bug in the gate must never brick
committing. The one hard-fail path is "source staged + review missing/stale".

### Install

**As a plugin**: `hooks/hooks.json` wires it via `${CLAUDE_PLUGIN_ROOT}`.

**Standalone (user settings)**: copy `hooks/scripts/nara-review-gate.py` to
`~/.claude/hooks/` and add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3 ~/.claude/hooks/nara-review-gate.py", "timeout": 10 }
        ]
      }
    ]
  }
}
```

### Roadmap

- **v2 — sha freshness**: instead of mtime, have `nara-code-review` stamp a
  `reviewed-diff-sha256` of `git diff HEAD` into its report, and have the gate
  compare against the current diff. Robust against mtime churn (formatters,
  branch switches) at the cost of a small skill change.
- **PR gate**: extend to `gh pr create` (diff = `base...HEAD`).
