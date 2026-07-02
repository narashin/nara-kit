---
name: memory-audit
description: >-
  Run a 4-signal scoring procedure on auto-memory files to detect stale or
  hallucination-risk entries. Audit each file 0-4 and flag for review.
  USE FOR: "memory-audit", "memory health", "메모리 점검", "stale memory", "환각 위험".
  DO NOT USE FOR: writing memories, code review, auto-removing memories.
---

# memory-audit

**UTILITY SKILL.** Score memory files. Flag risky.

## Signals (each = +1)

1. `age_days >= 90`
2. `ref_validity < 100%` — declared `ref_paths` missing on disk
3. `code_drift > 0` — referenced files changed after `verified_at`
4. `conflict_found` — newer memory has `supersedes:`/`replaces:`/`deprecates:` mention

## Score → Action

| Score | Label | Action |
|-------|-------|--------|
| 0 | healthy | keep |
| 1 | watch | review at next `/reflect` |
| 2 | suspect | manual decision |
| 3-4 | danger | archive or rewrite |

## Run

Iterate memory files under `~/.claude/projects/<slug>/memory/` (skip `MEMORY.md`). Run `"${CLAUDE_PLUGIN_ROOT:-.}/skills/memory-audit/scripts/audit.sh"` per file (the plugin-root prefix makes it resolve from any consuming project's cwd). Aggregate JSON, sort by score desc.

Full algorithm + script contract → [scoring.md](references/scoring.md).

## Frontmatter

```yaml
verified_at: 2026-05-18      # ISO; falls back to mtime
ref_paths: [docs/x.md, ...]  # explicit refs; grep-fallback noisy
```

## Receipt

```
status: audited
total: 12 | healthy: 8 | watch: 2 | suspect: 1 | danger: 1
flagged: foo.md (score=3, age,ref_validity,drift) → archive
next: archive or update flagged
```

## Examples

- All healthy → `total: 5 | healthy: 5`.
- Danger → signals.
- No memory dir → `❌ 실패`.

## Troubleshooting

- Needs `jq`, `git`. `ref_paths` resolve from project root. `verified_at` = `YYYY-MM-DD`.
