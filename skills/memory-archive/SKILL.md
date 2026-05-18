---
name: memory-archive
description: >-
  Archive a flagged auto-memory file by moving it to memory/archive/ and
  removing its line from MEMORY.md. Reversible — never deletes.
  USE FOR: "memory-archive", "메모리 archive", "stale memory 정리", "archive memory",
  "환각 위험 메모리 격리".
  DO NOT USE FOR: scoring (use memory-audit), permanent delete (manual rm only),
  writing new memories.
---

# memory-archive

**UTILITY SKILL.** Archive a flagged memory file. Move only, never delete.

## Preconditions

1. Memory was already flagged by `/memory-audit` (score >= 2).
2. User explicitly approved the archive (AskUserQuestion or direct invocation).
3. File path resolves under `~/.claude/projects/<slug>/memory/`.

## Behavior

- Move `<mem>/<file>.md` → `<mem>/archive/<file>.md`.
- Remove the matching line from `<mem>/MEMORY.md` index.
- Idempotent — re-running on already-archived path returns `action: noop`.
- File-name collision → append timestamp suffix (`.YYYYMMDD-HHMMSS.md`).

## Run

```bash
bash skills/memory-archive/scripts/archive.sh <memory_file>
```

Receipt JSON:

```json
{"action": "archived", "from": "...", "to": ".../archive/...", "index_updated": true}
```

## Restore

Restore is manual. Move file back from `archive/` and re-add the index line:

```bash
mv memory/archive/foo.md memory/foo.md
echo '- [Foo](foo.md) — restored' >> memory/MEMORY.md
```

## Examples

- Archive flagged → `action: archived, index_updated: true`.
- Already in archive → `action: noop`.
- Restore = manual mv + MEMORY.md edit.

## Troubleshooting

- Needs `jq`, `mv`, `grep`, `sed`.
- File not found → `❌ 실패`.
- Permission denied → check memory dir ownership.

## Companion skills

- `memory-audit` — score first, archive second.
- `/reflect` — surfaces flagged memories with archive prompts.
