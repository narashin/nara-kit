# EPT Evaluation Axes

## Axis Table

| Axis | How to capture | Meaning |
|---|---|---|
| Success/failure | Did executor produce intended deliverable (binary) | Minimum bar |
| Accuracy | What % of requirements satisfied | Partial success degree |
| Step count | Tool-call / decision-step count | Instruction waste indicator |
| Duration | Executor's duration_ms | Cognitive load proxy |
| Retry count | Same decision redone count | Instruction ambiguity signal |
| Unclear points | Executor enumerates as bullets | Qualitative improvement material |
| Discretionary fill-ins | Decisions not fixed by instruction | Surfaces implicit specification |

**Weighting**: Qualitative (unclear points / discretionary fill-ins) is primary, quantitative (time / step count) is auxiliary.

## Qualitative Interpretation of `tool_uses`

Using `tool_uses` as a **relative value across scenarios** reveals structural defects:

- If one scenario is **3-5x+ vs others**, the skill has **low self-containment**. Executor forced into reference descent.
- Typical: all scenarios have 1-3 `tool_uses` but one has 15+ -> no recipe for that scenario in the skill itself
- Fix: add inline minimum complete example or guidance at top of SKILL.md -> significantly drops `tool_uses`

Even at 100% accuracy, `tool_uses` skew is grounds for triggering iter 2.

## Fix Propagation Patterns

- **Conservative swing** (estimate > actual): one fix aimed at multiple axes but only moved one
- **Overshoot** (estimate < actual): one structural piece satisfied multiple axes at once
- **Zero-shoot** (estimate > 0, actual = 0): fix inferred from axis name did not reach judgment wording

Before applying diff, have subagent verbalize "which judgment wording this fix satisfies". When adding new evaluation axes, concretize judgment criteria to threshold-wording level.

## Iteration Stopping Criteria

**Convergence (stop)**: 2 consecutive rounds with ALL of:
- New unclear points: 0
- Accuracy improvement vs previous: +3 points or less
- Step count variation: within +/-10%
- Duration variation: within +/-15%
- **Overfitting check**: add 1 hold-out scenario at convergence. If accuracy drops 15+ points, overfitting detected -> redesign scenarios.

**Divergence (suspect design)**: new unclear points do not decrease across 3+ iterations -> rewrite structure, not patches.

**Resource cutoff**: stop when importance and improvement cost no longer balance.

## Variant Exploration (optional, plateau-breaking)

When approaching plateau but not meeting 2-consecutive-clear criteria:
- **Conservative variant**: current prompt + next-best minor fix
- **Exploratory variant**: structural change (reorder sections, split paragraphs, add worked example)

Dispatch fresh subagents on same scenarios in parallel. Keep variant with higher accuracy; tie-break: fewer unclear points, then lower `tool_uses`.

Pairwise-comparison caveats:
- Do NOT ask subagent to rate "A vs B" directly (position bias)
- Compare on objective axes only
- If qualitative comparison needed: counterbalance both orderings
