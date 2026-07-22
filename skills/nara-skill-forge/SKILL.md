---
name: nara-skill-forge
description: >-
  Improve, harden, or benchmark an agent skill: Waza static analysis + eval
  graders + EPT subagent execution with a working-tree regression ratchet.
  USE FOR: "skill 개선해줘", "스킬 개선해줘", "스킬 강화", "improve skill", "harden skill",
  "benchmark skill", "forge skill". DO NOT USE FOR: toolkit friction reports
  (use nara-meta-feedback), tuning non-skill prompts (use
  nara-empirical-prompt-tuning), authoring a brand-new skill from scratch.
---

# Skill Forge

`check → scaffold → execute → grade → fix (ratchet) → converge` — no fix ships
that makes the skill worse.

## Prerequisites

- `waza` CLI (`which waza`)
- Target skill has SKILL.md (`evals/` scaffolding is Phase 1's job)

## Phase 0: Static Analysis + Gates

Run without user input:

```bash
which waza && waza check skills/<name> && waza tokens count skills/<name>
```

Extract: compliance score, tokens vs budget, spec violations, advisories.

**`waza` missing/broken** (`which waza` fails, or commands error) → do not
fabricate scores. Either stop and ask the user to install waza, or run the
manual path: hand-audit frontmatter + link targets + body length, and grade via
the Phase 3 manual text/code graders. Mark the whole run `dry_run` in that case.

**Runtime-neutrality gate** — nara-kit ships the same SKILL.md to Claude Code and
Codex; scan for single-runtime lock: [runtime-gate.md](references/runtime-gate.md).
Any hit → Phase 4 round-1 P0 fix.

## Phase 1: Scaffold or Verify Eval

waza's LLM-backed commands need Copilot; its deterministic half does not. Default
to the no-Copilot path — the running agent IS the LLM layer:

- No `evals/` → `waza init .`, then `waza new eval` to scaffold.
- No tasks yet → author 2-4 task yamls yourself from the skill body (happy path
  + one edge/scope case), deterministic text/code graders only — never LLM-judge
  graders. `waza suggest skills/<name>` is an optional shortcut when Copilot
  exists; on parse failure, author manually.
- Tasks exist → `waza check skills/<name>` validates schema.

eval.yaml must use `executor: mock` — real execution is handled by Phase 2.

**Validate every grader before trusting it** (graders are the ratchet's only
truth — a hollow one makes every later score meaningless). For each grader, hand
it one plausibly-correct output and one plausibly-wrong output: it MUST pass the
first and fail the second. A grader that passes both (too loose) or fails both
(too strict, e.g. exact-string / wrong-language / rejects an answer for quoting a
rule) is a false proxy — fix or drop it before Phase 2.

## Phase 2: EPT Execute

For each task in `evals/<name>/tasks/*.yaml`:

1. Read task `inputs.prompt`.
2. Dispatch a fresh subagent per run with: the skill's SKILL.md as context, the
   task prompt as the scenario, and `inputs.files` read from `fixtures/`. Run
   each task **twice** (two fresh subagents) — one run is noisy signal; if the
   two disagree on any grader, treat that task as unresolved, not passed.
3. Collect per run: output text, `tool_uses`, `duration_ms`, self-reported
   unclear points + discretionary fills.

Write results in the `waza run` output schema — the mechanical field-mapping
(mock probe, `runs[]` overwrite) lives in [reporting.md](references/reporting.md#results-schema).

## Phase 3: Grade

```bash
waza grade evals/<name>/eval.yaml --results results/forge-iter-N.json
```

Fallback (format rejected): run text/code graders manually, report pass/fail per
grader per task. Combine objective (grader pass/fail) with qualitative (unclear
points, discretionary fills). Record per-task scores as the ratchet baseline.

🛑 Benchmark-only — if the user asked not to modify, in ANY phrasing ("벤치마크만",
"고치지 마", "평가만", "benchmark only"), STOP here: report Phases 0-3, mark
Fix/Convergence lines `N/A — benchmark-only`, change nothing.

🔴 CHECKPOINT — otherwise present the baseline report + planned fix themes; wait
for user approval before Phase 4.

## Phase 4: Fix (Ratcheted)

Snapshot the SKILL.md, apply ONE theme, re-grade with a fresh subagent, then
keep-or-restore. Full mechanics + exception table: [ratchet.md](references/ratchet.md).

Fix priority:

1. Failed graders → body teaches the wrong behavior
2. Unclear points → wording is ambiguous
3. Discretionary fills → skill is silent where it should guide
4. waza check findings → structural / compliance issues

One theme per iteration.

## Phase 5: Converge

- **Converged** (stop): 2 consecutive iterations with all graders pass + 0 new
  unclear + no new waza violations.
- **Diverged** (escalate): 3+ iterations without grader improvement.
- **Cutoff**: ship when the `waza grade` overall score ≥ 0.8 (stdout
  `overall_score` / merged-output `aggregate_score`, 0-1 scale) but improvement
  plateaus.

🛑 STOP at verdict — present the final SKILL.md diff + per-iteration ratchet log
(kept/restored). The user decides whether to commit; never auto-commit.

## Reporting

Print the per-iteration report after every iteration; format block +
step-by-step worked example: [reporting.md](references/reporting.md).

## Example

`"nara-commit 강화해줘"` → the full six-phase trace (check → converge) is walked
step by step in [reporting.md](references/reporting.md#worked-example).

## Troubleshooting

| Trigger | First fix | Still fails → fallback |
|---|---|---|
| Fix regresses another task | ratchet restores the snapshot | next-lowest theme; never retry the same one |
| Re-grade subagent times out | retry once, fresh subagent | mark `dry_run`; never keep a fix on dry-grade |
| `waza grade` rejects results | reshape to the Phase 2 schema | probe it via `waza run … -o` on mock |
| Fix grows the token budget | restore — bloat is a regression | offload prose to a `references/*.md` module |

## Anti-Patterns

- Do NOT run `waza run` with the `copilot-sdk` executor, and never authenticate
  Copilot when prompted — use EPT subagents (avoids auth + shared-pool billing).
- Do NOT reuse subagents across iterations — fresh agent each time.
- Do NOT batch unrelated fixes per iteration.
- Do NOT skip `waza check` even if graders pass — structural issues matter.
- Do NOT keep a regressing or token-growing fix — the ratchet restores it.
- Do NOT hardcode a single runtime in the body ([runtime-gate.md](references/runtime-gate.md)).
