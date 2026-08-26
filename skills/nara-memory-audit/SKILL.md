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

- `<agent-config>/projects/<slug>/memory/*.md` — skip `MEMORY.md` + `archive/`. Default = all files (cheap).
- Run from the repo the memories are ABOUT (git resolves there); `CLAUDE_PROJECT_DIR` if cwd differs. Skill refs fall back to the agent skill roots, so a repo with no `skills/` tree still works — at reduced path-claim precision (see Rules).

## Procedure

1. **Tier 1** (bash, ~0 tokens): run `audit.sh` on each target; each scores 0-4 across `age_days>=90` / `ref_validity<100%` / `code_drift>0` / `skill_ref_broken`. Sort desc. `0`=healthy, `1`=watch, **`2+`=flagged**.
2. **Tier 2** (flagged only): batch (~5-8/agent), dispatch parallel subagents → per file `verdict ∈ {FRESH, STALE, CONTRADICTION, UNVERIFIABLE}` + evidence + minimal fix. Principle with no anchor → FRESH.
3. **Report** (receipt) — nothing modified.
4. **Approval gate** — explicit go; accept all/subset/none. This keeps the skill a doubt-generator, not a judge ([[nara-kit-thesis-direction]]).
5. **Apply**: anchor fix → `Edit` (slim, don't just patch — [[feedback-memory-storage-discipline]]); danger/refuted → move to `memory/archive/` + drop its `MEMORY.md` line; re-sync index (pointers == files).
6. **Mirror the removal** — `nara-reflect` dual-stores (file + MCP record), so archiving the file alone leaves a live twin that still gets recalled. Supersede or delete each MCP counterpart in the same approved batch; no MCP tool → skip and say so.

## Examples

- Clean repo → `total: N | healthy: N`, stop (no Tier 2).
- Post-migration → `skill_ref_broken` → Tier 2 confirms STALE → fix paths on approval.
- Spent one-off memory (old + dead refs) → `danger` → archive on approval.

## Receipt

```
status: audited
scope: <MEM_DIR>  |  total: 31 | healthy: 21 | watch: 4 | suspect: 4 | danger: 2
flagged (6):
  jira_triage.md   score=2  ref_validity      STALE          → skills/nara-jira-triage/
  runtime_cost.md  score=2  age,code_drift    CONTRADICTION  → aoe→herdr
  offload_talk.md  score=3  age,ref_validity  STALE(spent)   → archive
applied: 4 fixed, 2 archived  |  MEMORY.md: 31→29 synced  |  mirror: 6 MCP records updated/superseded
```

## Rules

- **No mutation before approval.** Tier 1 + Tier 2 read-only.
- **Move, never delete** — archive reversible; `rm` is manual + explicit only.
- External-system claims = `UNVERIFIABLE`, never guessed.
- **Declare three coverage limits; never claim a full sweep.** (a) Tier 1 is bash and cannot read an MCP store — a record that only ever existed there is invisible. (b) A bare backticked skill name (no `skills/` prefix, no `/nara-`) is a Tier-2-only catch. (c) Outside the toolkit repo a `skills/<name>/` claim is only refutable when the skill is gone entirely; renamed-but-installed returns `unknown`.
- **Unresolvable ≠ broken, but absent-everywhere IS broken.** `skill_ref_unknown` (score 0) means only "the skill exists, this repo can't confirm the path". A skill missing from every root is drift whichever repo asked.
- **Never delete a true anchor to silence a signal.** A `ref_validity` miss on a present file means the reader is wrong — fix the reader; dropping the path disarms signals 2-3 for good.

## Troubleshooting

- `❌ 실패: memory dir 없음 — <path>` → check `<agent-config>/projects/<slug>/memory/`.
- Needs `jq` + `git`; macOS-only (`stat -f`, `date -j`) — on Linux every call exits 1 with no JSON.
- Skill refs `unknown` and you want them decided? Point `CLAUDE_PROJECT_DIR` at the toolkit repo — that, not `NARA_SKILLS_DIRS`, is what decides a `skills/<name>/` path claim. `NARA_SKILLS_DIRS` only replaces the root probe list (Form B, and the absent-everywhere fallback).
