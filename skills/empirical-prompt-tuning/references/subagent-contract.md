# EPT Subagent Invocation Contract

The prompt given to the executor takes this structure:

```
You are an executor reading <target prompt name> with a blank slate.

## Target prompt
<Paste the full body of the target prompt, or specify a path for Read>

## Scenario
<One paragraph setting the scenario context>

## Requirements checklist (items the deliverable must satisfy)
1. [critical] <item that belongs to the minimum bar>
2. <normal item>
3. <normal item>
...
(At least one [critical] is required.)

## Task
1. Follow the target prompt to execute the scenario and produce the deliverable.
2. On completion, respond with the report structure below.

## Report structure
- Deliverable: <artifact or execution summary>
- Requirement achievement: O / X / partial (with reason) for each item
- **Trace** (tag OK / stuck / skipped for each phase, one-line reason when not OK):
  - Understanding (reading the instruction and building a mental model)
  - Planning (deciding the approach / ordering)
  - Execution (actually doing the work)
  - Formatting (shaping the deliverable to the expected form)
  - *Collapsed form allowed*: when all four phases are OK, `Trace: all OK` is sufficient.
- **Unclear points (structured)**: for each issue:
  - Issue: <what observably happened>
  - Cause: <why, at the instruction level>
  - General Fix Rule: <class-level rule, not a spot fix>
- Discretionary fill-ins: places not fixed by instruction, filled by own judgment (bullets)
- Retries: number of times same decision was redone and why
```

The caller extracts self-report from the report and fills the evaluation-axis table by obtaining `tool_uses` / `duration_ms` from the Agent tool's usage meta.
