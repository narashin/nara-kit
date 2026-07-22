# Reporting Format

Print this block after EVERY iteration as it completes — never withhold interim
results until convergence.

```
## Forge Iteration N
### Static (waza check): Compliance {s} · Tokens {n}/{b} · Violations {list}
### Execution (EPT): | Task | Pass | Score | Steps | Duration | Unclear |
### Qualitative: Unclear {list} · Discretionary {list}
### Fix: {theme} → ratchet {kept | restored}
(Convergence: {N}/2 consecutive clears)
```

For a benchmark-only run, print Phases 0-3 only and set the Fix/Convergence lines
to `N/A — benchmark-only`.

## Results schema

`waza grade` rejects a flat `task_id`/`output` list — results must match the
`waza run` output shape. Steps:

1. Probe once on the mock executor:
   `waza run evals/<name>/eval.yaml -o results/schema-probe.json`.
2. The probe file arrives with every `tasks[].test_id` pre-filled. Per task,
   overwrite `runs[0].final_output` (subagent output), `runs[0].duration_ms`, and
   `runs[0].session_digest.tool_call_count` with measured values.
3. Save as `results/forge-iter-N.json` and grade it.

## Worked example

`"nara-commit 강화해줘"` → Phase 0 check + gate → author 3 tasks → EPT run (task-2
grader fails) → snapshot, add one rule, re-grade with a fresh subagent, others
hold → kept → iter 2 clean → converged → 🛑 STOP, present diff, await commit.
