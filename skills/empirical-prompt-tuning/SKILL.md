---
name: empirical-prompt-tuning
description: >-
  This skill should be used when the user asks to "tune a prompt",
  "evaluate a skill", "test prompt quality", "run empirical evaluation",
  "/empirical-prompt-tuning", or when a skill / slash command / task prompt /
  CLAUDE.md section has been newly created or significantly revised and
  needs objective quality validation through unbiased execution.
---

# Empirical Prompt Tuning

Prompt quality is invisible to the author. The clearer a prompt feels to the writer, the more likely another agent stumbles on it. **Have an unbiased executor actually run the prompt, evaluate from both sides (executor self-report + instructor-side metrics), and iterate until convergence.** Do not stop until improvement plateaus.

## When to Use

- Immediately after creating or significantly revising a skill / slash command / task prompt
- When an agent does not behave as expected and the cause is suspected to be instruction ambiguity
- When hardening a high-importance prompt (frequently used skill, core automation prompt)

Do NOT use for:
- Throwaway one-shot prompts (evaluation cost exceeds benefit)
- When the goal is reflecting the author's subjective preference, not improving success rate

## Workflow

### 0. Iteration 0 — Description/Body Alignment Check (static, no dispatch)

- Read the frontmatter `description` triggers and stated purpose
- Read the body's actual coverage
- If there is a gap, align description or body before proceeding to iter 1
- Example: description says "navigation / form filling / data extraction" but body only covers `npx playwright test` CLI reference
- Skipping this step causes subagents to "reinterpret" the body to match the description, producing false positives where the skill appears to meet requirements it actually doesn't

### 1. Baseline Preparation

Finalize the target prompt and prepare two things:
- **Evaluation scenarios** (2–3): one median case + 1–2 edge cases. Realistic tasks where the target prompt would actually be applied.
- **Requirements checklist** (for accuracy calculation): 3–7 items per scenario defining what the output must satisfy. Accuracy % = satisfied items / total items. Fix these upfront — do not adjust afterward.

### 2. Bias-Free Reading

Have a "blank slate" executor read the instructions. **Dispatch a new subagent** via the Agent tool. Never self-review (objectively reading text you just wrote is structurally impossible). When running multiple scenarios in parallel, place multiple Agent calls in a single message. For environments where dispatch is unavailable, see "Environment Constraints" section.

### 3. Execution

Pass a prompt following the **Subagent Launch Contract** (below) to the subagent and have it execute the scenario. The executor generates implementation or output, then returns a self-report.

### 4. Two-Sided Evaluation

Record the following from the returned results:

**Executor self-report** (extracted from subagent report):
- Unclear points / discretionary fills / template application difficulties

**Instructor-side measurement** (judgment rules are canonically defined here; other sections reference this one):
- Success/failure: success (○) only when **all** `[critical]`-tagged requirements are ○. If any is × or partial, it's failure (×). Binary only.
- Accuracy: requirements checklist achievement rate %. ○ = 1, × = 0, partial = 0.5, divided by total items.
- Step count: `tool_uses` from Agent tool usage metadata. Include Read/Grep — do not exclude.
- Duration: `duration_ms` from Agent tool usage metadata.
- Retry count: times the subagent reconsidered the same decision. Extracted from self-report (not measurable instructor-side).
- **On failure: add "which [critical] item failed" to the "unclear points" section of the presentation format** (for root cause tracking).

Requirements checklists must include **at least 1** `[critical]`-tagged item (0 makes success judgment vacuous). Do not add/remove [critical] tags after the fact.

### 5. Delta Application

Apply the minimum fix that resolves unclear points. One iteration = one theme (related multiple fixes OK; unrelated fixes go to next iteration).
- **Before applying: explicitly state which requirements checklist / judgment criteria items this fix addresses** (fixes inferred from axis names alone often miss. See "Fix Propagation Patterns" section).

### 6. Re-evaluation

Run steps 2→5 again with a **new** subagent (do not reuse — the previous agent has learned from prior improvements). Increase parallelism only when improvement doesn't plateau as iterations progress.

### 7. Convergence Check

Guideline: "2 consecutive iterations with zero new unclear points AND metric improvement below threshold (see below)." For high-importance prompts, require 3 consecutive.

## Evaluation Axes

| Axis | Measurement | Meaning |
|---|---|---|
| Success/failure | Did the executor produce the intended output (binary) | Minimum bar |
| Accuracy | What % of requirements did the output satisfy | Degree of partial success |
| Step count | Tool calls / decision steps used by executor | Instruction waste indicator |
| Duration | Executor's duration_ms | Cognitive load proxy |
| Retry count | Times the same decision was reconsidered | Ambiguity signal |
| Unclear points (self-report) | Executor lists items | Qualitative improvement material |
| Discretionary fills (self-report) | Decisions made where instructions were silent | Implicit spec exposure |

**Weighting**: qualitative (unclear points, discretionary fills) is primary; quantitative (duration, step count) is supplementary. Chasing time reduction alone makes prompts too thin.

### Qualitative Interpretation of `tool_uses`

Accuracy alone hides skill problems. Using `tool_uses` as a **relative value across scenarios** reveals structural flaws:

- If one scenario is **3–5x higher** than others, the skill is **decision-tree-index-heavy with low self-containment**. The executor is forced into references descent.
- Typical example: all scenarios have `tool_uses` of 1–3, but one scenario has 15+ → no recipe for that scenario exists in the skill; executor is cross-searching references/.
- Fix: in iter 2, add "minimal complete example inline" or "when to read references" guidance to the top of SKILL.md — `tool_uses` drops significantly.

Even at 100% accuracy, `tool_uses` skew justifies triggering iter 2. "Judge by accuracy alone and stop" misses structural flaws.

### Fix Propagation Patterns (Conservative / Upswing / Zero)

Fix → effect is not linear. Three patterns can occur:

- **Conservative** (estimate > actual): targeted multiple axes with one fix, but only one moved. "Multi-axis targeting tends to miss."
- **Upswing** (estimate < actual): one structural piece of information (e.g., command + config + expected output combo) simultaneously satisfies multiple judgment criteria. "Information combos are structurally multi-axis effective."
- **Zero** (estimate > 0, actual = 0): fix inferred from axis name didn't reach any judgment criteria. "Axis names and judgment criteria are different things."

To stabilize: **before applying deltas, have the subagent verbalize "which judgment criteria this fix satisfies."** Without threshold-level linkage, estimate accuracy won't materialize. When creating new evaluation axes, also concretize each point's judgment criteria to threshold-level ("all explicitly stated", "full working minimal configuration" — granularity where a subagent can determine what earns 2 points).

## Subagent Launch Contract

The prompt passed to the executor follows this structure. This is the input contract for "two-sided evaluation."

```
You are an executor reading <target prompt name> from a blank slate.

## Target Prompt
<Full text of target prompt OR file path for Read>

## Scenario
<Scenario setup, one paragraph>

## Requirements Checklist (what the output must satisfy)
1. [critical] <item included in minimum bar>
2. <normal item>
3. <normal item>
...
(Judgment rules are canonically defined in "Workflow 4. Two-Sided Evaluation / Instructor-side measurement". At least 1 [critical] required.)

## Task
1. Execute the scenario following the target prompt. Generate the output.
2. When done, respond with the report structure below.

## Report Structure
- Artifact: <generated output or execution result summary>
- Requirements: for each item, ○ / × / partial (with reason)
- Unclear points: parts of the target prompt where you got stuck or found wording ambiguous (bullet list)
- Discretionary fills: decisions you made where the instructions were silent (bullet list)
- Retries: how many times you reconsidered the same decision, and why
```

The caller extracts the self-report portion from the report and obtains `tool_uses` / `duration_ms` from the Agent tool's usage metadata to fill the evaluation axis table.

## Environment Constraints

When new subagent dispatch is unavailable (already running as a subagent, Task tool disabled, etc.), **do not apply this skill**.
- Alternative 1: ask the user to launch a separate Claude Code session
- Alternative 2: abandon evaluation and explicitly report "empirical evaluation skipped: dispatch unavailable"
- **NOT OK**: substitute with self-review (bias makes the evaluation results untrustworthy)

**Structural Audit Mode**: when checking only the **description/body consistency and clarity** of a skill/prompt (not empirical evaluation), explicitly separate this as structural audit mode. Include "This is structural audit mode: text consistency check, not execution" in the subagent prompt. This lets the subagent bypass the environment constraints skip behavior and return a static review. Structural audit is supplementary to empirical, not a substitute (cannot be used for consecutive-clear determination).

## Iteration Termination Criteria

- **Convergence (stop)**: 2 consecutive iterations satisfying **all** of:
  - New unclear points: 0
  - Accuracy improvement vs. previous: ≤ +3 points (saturation like 5% → 8%)
  - Step count change vs. previous: within ±10%
  - Duration change vs. previous: within ±15%
  - **Overfitting check**: at convergence, evaluate with 1 previously unused hold-out scenario. If accuracy drops 15+ points below recent average, it's overfitting. Return to baseline scenario design and add edges.
- **Divergence (question the design)**: 3+ iterations without reducing new unclear points → the prompt's design approach itself may be wrong. Stop patching; rewrite the structure.
- **Resource cutoff**: stop when importance and improvement cost no longer balance (ship at 80 points).

## Presentation Format

Record and present to the user in this format per iteration:

```
## Iteration N

### Changes (delta from previous)
- <fix description, one line>

### Execution Results (per scenario)
| Scenario | Success/Failure | Accuracy | steps | duration | retries |
|---|---|---|---|---|---|
| A | ○ | 90% | 4 | 20s | 0 |
| B | × | 60% | 9 | 41s | 2 |

### Unclear Points (newly surfaced this iteration)
- <Scenario B>: [critical] item N was × — <reason, one line>   # mandatory on failure
- <Scenario B>: <other issue, one line>
- <Scenario A>: (none new)

### Discretionary Fills (newly surfaced this iteration)
- <Scenario B>: <fill description>

### Next Fix
- <minimum fix, one line>

(Convergence check: X consecutive clears / Y iterations until stop condition)
```

## Red Flags (Watch for Rationalization)

| Rationalization that appears | Reality |
|---|---|
| "Re-reading it myself has the same effect" | Objectively viewing text you just wrote is impossible. Always dispatch a new subagent. |
| "One scenario is enough" | One scenario overfits. Minimum 2, preferably 3. |
| "Unclear points hit zero once, so we're done" | Could be coincidence. Require 2 consecutive. |
| "Let's fix all unclear points at once" | Can't tell what worked. One iteration, one theme. |
| "Let's split every related micro-fix into its own iter" | Opposite trap. "One theme" is a semantic unit. 2–3 related micro-fixes can be one iter. Over-splitting explodes iter count. |
| "Metrics are good so ignore qualitative feedback" | Time reduction can signal over-thinning. Qualitative is primary. |
| "Rewriting from scratch is faster" | Correct if unclear points don't decrease after 3+ iters. Before that, it's avoidance. |
| "Let's reuse the same subagent" | It learned from prior improvements. Dispatch fresh every time. |

## Common Failures

- **Scenario too easy / too hard**: neither produces signal. One median real-world case + one edge case.
- **Metrics-only judgment**: chasing time reduction strips important explanations, making the prompt brittle.
- **Too many changes per iteration**: "which fix from that batch worked?" becomes untraceable. One fix per iteration.
- **Tuning scenarios to match fixes**: making scenarios easier to hide unclear points → defeats the purpose.
