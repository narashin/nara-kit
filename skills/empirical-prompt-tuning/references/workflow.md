# EPT Workflow Steps

## Step 0: Description/Body Consistency Check (static, no dispatch)

- Read the triggers/use cases claimed by the frontmatter `description`
- Read the scope the body actually covers
- If there is a gap, reconcile description or body before moving to iter 1
- Example: description says "navigation / form filling / data extraction" but the body is only a CLI reference for `npx playwright test` -- detect that kind of gap
- If skipped, the subagent will "reinterpret" the body to match the description, causing false positives

## Step 1: Baseline Preparation

Fix the target prompt and prepare:
- **Evaluation scenarios** (2-3): 1 median + 1-2 edge. Realistic tasks for actual use.
- **Requirements checklist**: 3-7 items per scenario. Accuracy % = satisfied / total. Fix in advance.
- At least one `[critical]`-tagged item required (else success judgment is vacuous).

## Step 2: Bias-Free Read

Dispatch a new subagent via Agent tool. Do NOT self-reread (structurally impossible to view own text objectively). Multiple scenarios can run in parallel via multiple Agent invocations in a single message.

## Step 3: Execution

Hand subagent a prompt following the subagent invocation contract (see references/subagent-contract.md). Executor produces output + self-report.

## Step 4: Two-Sided Evaluation

Record from results:
- **Executor self-report**: unclear points, discretionary fill-ins, stuck points
- **Trace interpretation**: tag each unclear point with originating phase (Understanding/Planning/Execution/Formatting)
- **Structured reflection**: each unclear point returned as `Issue / Cause / General Fix Rule`
- **Instruction-side measurements**:
  - Success/failure: binary. All `[critical]` items must be met for success.
  - Accuracy: % of requirements checklist (full=1, partial=0.5, miss=0)
  - Step count: `tool_uses` from Agent tool usage meta
  - Duration: `duration_ms` from Agent tool usage meta
  - Retry count: from subagent self-report
  - On failure: note which `[critical]` item dropped

## Step 5: Apply the Diff

Minimum fix to eliminate unclear points. One theme per iteration (related fixes OK, unrelated go next).
- Before applying, state "which checklist item / judgment wording this fix satisfies"
- Consult failure pattern ledger first (see references/ledger.md)

## Step 6: Re-Evaluate

Run steps 2-5 with a NEW subagent (never reuse -- it learned previous improvements). Increase parallelism if not plateauing.

## Step 7: Convergence Check

Stop when 2 consecutive iterations have zero new unclear points AND metric improvements below thresholds. Use 3 consecutive for high-importance prompts.

## Environment Constraints

When subagent dispatch is unavailable:
- Alternative 1: ask user to start separate session for evaluation
- Alternative 2: report "empirical evaluation skipped: dispatch unavailable"
- **NG**: self-reread (bias invalidates results)

**Structural review mode**: for consistency/clarity check only (no execution). Note clearly in subagent prompt "structural review mode: text consistency check, not execution".
