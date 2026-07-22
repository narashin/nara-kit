---
name: nara-empirical-prompt-tuning
description: >-
  Iterate and improve agent-facing instructions by dispatching bias-free executors and evaluating two-sidedly until improvements plateau.
  USE FOR: "프롬프트 튜닝", "EPT", "prompt tuning", "improve prompt".
  DO NOT USE FOR: skill improvement/hardening/benchmark (use nara-skill-forge), one-off throwaway prompts, subjective style preferences, direct skill authoring (use skill-development).
---

# Empirical Prompt Tuning

The author of a prompt cannot judge its quality. This skill has a **bias-free executor actually run the instruction, evaluates two-sidedly, and iterates** until improvements plateau.

## Core Loop

0. **Iter 0 -- static check**: verify description/body consistency (no dispatch needed). Reconcile gaps before iter 1.
1. **Prepare**: fix target prompt, create 2-3 evaluation scenarios (1 median + edges), define requirements checklist (3-7 items, at least one `[critical]`).
2. **Dispatch**: new subagent via Agent tool (never self-reread). Parallel scenarios OK.
3. **Execute**: subagent runs scenario per contract, returns self-report.
4. **Evaluate two-sided**: executor self-report (unclear points, discretionary fill-ins) + instruction-side metrics (success, accuracy, steps, duration, retries). Tag unclear points by phase.
5. **Fix**: minimum diff, one theme per iteration. Check failure pattern ledger first.
6. **Re-evaluate**: new subagent (never reuse). Repeat 2-5.
7. **Converge**: stop at 2 consecutive rounds with zero new unclear points and metrics below thresholds.

**Environment constraint**: if subagent dispatch unavailable, do NOT self-reread. Report "empirical evaluation skipped" or delegate to separate session.

## References

- [Workflow steps](references/workflow.md)
- [Evaluation axes and stopping criteria](references/evaluation-axes.md)
- [Subagent invocation contract](references/subagent-contract.md)
- [Failure pattern ledger](references/ledger.md)
- [Presentation format and red flags](references/presentation-format.md)
