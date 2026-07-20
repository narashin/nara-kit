---
name: nara-skill-forge
description: "Use when improving, hardening, or benchmarking a Claude Code skill. Combines Waza static analysis + eval graders with EPT subagent execution and a working-tree regression ratchet for iterative skill improvement. Triggers on: 'skill 개선해줘', '스킬 강화', 'improve skill', 'harden skill', 'benchmark skill', 'forge skill'."
---

# Skill Forge

Waza (static + graders) + EPT (subagent execution) loop with a regression ratchet
— no fix ships that makes the skill worse.

`check → scaffold → execute → grade → fix (ratchet) → converge`

## Prerequisites

- `waza` CLI (`which waza`)
- Target skill has SKILL.md; Waza project initialized (`waza init` if no `evals/`)

## Phase 0: Static Analysis + Gates

Run without user input:

```bash
waza check skills/<name>
waza tokens count skills/<name>
```

Extract: compliance score, tokens vs budget, spec violations, advisories.

**Runtime-neutrality gate** — nara-kit ships the same SKILL.md to Claude Code and
Codex; scan for single-runtime lock: [runtime-gate.md](references/runtime-gate.md).
Any hit → Phase 4 round-1 P0 fix. If no `evals/`, run `waza init .` first.

## Phase 1: Scaffold or Verify Eval

- No tasks yet → `waza suggest skills/<name>`.
- Tasks exist → `waza check skills/<name>` validates schema.

eval.yaml must use `executor: mock` — real execution is handled by Phase 2.

## Phase 2: EPT Execute

For each task in `evals/<name>/tasks/*.yaml`:

1. Read task `inputs.prompt`.
2. Dispatch a fresh subagent with: the skill's SKILL.md as context, the task
   prompt as the scenario, and `inputs.files` read from `fixtures/`.
3. Collect: output text, `tool_uses`, `duration_ms`, and self-reported unclear
   points + discretionary fills.

Save to `results/forge-iter-N.json`:

```json
{"task_id": "<from task yaml>", "output": "<subagent response>", "duration_ms": 0, "tool_calls": 0, "status": "completed"}
```

## Phase 3: Grade

```bash
waza grade evals/<name>/eval.yaml --results results/forge-iter-N.json
```

Fallback (format rejected): run text/code graders manually, report pass/fail per
grader per task. Combine objective (grader pass/fail) with qualitative (unclear
points, discretionary fills). Record per-task scores as the ratchet baseline.

## Phase 4: Fix (Ratcheted)

Snapshot the SKILL.md, apply ONE theme, re-grade with a fresh subagent, then
keep-or-restore. Full mechanics + exception table: [ratchet.md](references/ratchet.md).

Fix priority:

1. Failed graders → body teaches the wrong behavior
2. Unclear points → wording is ambiguous
3. Discretionary fills → skill is silent where it should guide
4. waza check findings → structural / compliance issues

One theme per iteration. Never batch unrelated fixes.

## Phase 5: Converge

- **Converged** (stop): 2 consecutive iterations with all graders pass + 0 new
  unclear + no new waza violations.
- **Diverged** (escalate): 3+ iterations without grader improvement.
- **Cutoff**: ship at 80+ score if improvement plateaus.

## Presentation Format

```
## Forge Iteration N
### Static (waza check): Compliance {s} · Tokens {n}/{b} · Violations {list}
### Execution (EPT): | Task | Pass | Score | Steps | Duration | Unclear |
### Qualitative: Unclear {list} · Discretionary {list}
### Fix: {theme} → ratchet {kept | restored}
(Convergence: {N}/2 consecutive clears)
```

## Example

`"nara-commit 강화해줘"` → P0 check + gate → suggest 3 tasks → EPT run (task-2
grader fails) → snapshot, add rule, re-grade, others hold → kept → iter 2 clean →
converged.

## Troubleshooting

- **Fix broke another task** → ratchet restores the snapshot; next theme. Rules +
  exceptions: [ratchet.md](references/ratchet.md).
- **Re-grade subagent times out** → mark `dry_run`; never keep a fix on dry-grade.
- **`waza run` demands Copilot auth** → do not authenticate; use EPT subagents.

## Anti-Patterns

- Do NOT run `waza run` with the `copilot-sdk` executor — use EPT subagents
  (avoids GitHub Copilot auth + shared-pool billing).
- Do NOT reuse subagents across iterations — fresh agent each time.
- Do NOT batch unrelated fixes per iteration.
- Do NOT skip `waza check` even if graders pass — structural issues matter.
- Do NOT keep a fix that regresses any prior-passing grader or grows the token
  budget — the ratchet restores it ([ratchet.md](references/ratchet.md)).
- Do NOT hardcode a single runtime in the body ([runtime-gate.md](references/runtime-gate.md)).
