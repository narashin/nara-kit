---
name: nara-memory-audit
description: >-
  Audit durable auto-memory files for staleness in two tiers — bash prefilter, then subagent verify on flagged files, then human-approved fix/archive.
  USE FOR: "memory-audit", "메모리 감사", "메모리 점검", "stale memory", after a breaking rename / skill add-remove / migration.
  DO NOT USE FOR: writing memories (nara-reflect), permanent delete (manual rm), toolkit friction (nara-meta-feedback).
---

# nara-memory-audit

**UTILITY SKILL.** Score memory files, verify the suspect ones, fix/archive on approval. Standalone. Move, never delete.
INVOKES: `scripts/audit.sh` (Tier 1) · parallel subagents (Tier 2).

Full algorithm + Tier 2 prompt → [scoring.md](references/scoring.md).

## When to run

- On demand: `/nara-memory-audit [scope]`.
- **Event-driven** (highest value): once after a breaking event — mass rename, skill add/remove, format/deploy-model migration. A single such event is the dominant cause of memory rot ([[feedback-memory-event-driven-sweep]]).
- Day-to-day staleness is caught at recall time, not here.

## Target

- `~/.claude/projects/<slug>/memory/*.md` — skip `MEMORY.md` + `archive/`. Default = all files (cheap).
- Run from the repo the memories are ABOUT (so `skills/` + git resolve); set `CLAUDE_PROJECT_DIR` if cwd differs.

## Procedure

1. **Tier 1** (bash, ~0 tokens): run `audit.sh` on each target; each scores 0-4 across `age_days>=90` / `ref_validity<100%` / `code_drift>0` / `skill_ref_broken`. Sort desc. `0`=healthy, `1`=watch, **`2+`=flagged**.
2. **Tier 2** (flagged only): batch (~5-8/agent), dispatch parallel subagents → per file `verdict ∈ {FRESH, STALE, CONTRADICTION, UNVERIFIABLE}` + evidence + minimal fix. Principle with no anchor → FRESH.
3. **Report** (receipt) — nothing modified.
4. **Approval gate** — explicit go; accept all/subset/none. This keeps the skill a doubt-generator, not a judge ([[nara-kit-thesis-direction]]).
5. **Apply**: anchor fix → `Edit` (slim, don't just patch — [[feedback-memory-storage-discipline]]); danger/refuted → move to `memory/archive/` + drop its `MEMORY.md` line; re-sync index (pointers == files).

## Examples

- Clean repo → `total: N | healthy: N`, stop (no Tier 2).
- Post-migration → several `skill_ref_broken` flags → Tier 2 confirms STALE → fix skill paths on approval.
- Spent one-off memory (old + dead refs) → `danger` → archive on approval.

## Receipt

```
status: audited
scope: <MEM_DIR>  |  total: 31 | healthy: 21 | watch: 4 | suspect: 4 | danger: 2
flagged (6):
  jira_triage.md   score=2  ref_validity      STALE          → skills/nara-jira-triage/
  runtime_cost.md  score=2  age,code_drift    CONTRADICTION  → aoe→herdr
  offload_talk.md  score=3  age,ref_validity  STALE(spent)   → archive
applied: 4 fixed, 2 archived  |  MEMORY.md: 31→29 synced
```

## Rules

- **No mutation before approval.** Tier 1 + Tier 2 read-only.
- **Move, never delete** — archive reversible; `rm` is manual + explicit only.
- External-system claims = `UNVERIFIABLE`, never guessed.
- `skill_ref_broken` is high-precision: bare backticked names (no `skills/` prefix, no `/nara-`) are a Tier-2-only catch — a file scoring 0 on signals 1-3 with only bare-name drift is missed. State it; don't claim full coverage.

## Troubleshooting

- `❌ 실패: memory dir 없음 — <path>` → check `~/.claude/projects/<slug>/memory/`.
- Needs `jq` + `git`. Missing → `❌ 실패: jq/git 필요`.
- Signal 4 empty though drift exists? The ref lacks a `skills/` prefix or `/nara-` invocation → Tier 2 territory, not Tier 1.
