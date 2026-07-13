# EPT Presentation Format

Record and present to the user at each iteration:

```
## Iteration N

### Changes (diff from previous)
- <one-line fix content>
- Pattern applied: <pattern name from ledger, or "(new)">

### Execution results (per scenario)
| Scenario | Success/Failure | Accuracy | steps | duration | retries | Weak phase |
|---|---|---|---|---|---|---|
| A | O | 90% | 4 | 20s | 0 | -- |
| B | X | 60% | 9 | 41s | 2 | Execution |

### Structured reflection (newly surfaced this time)
- <Scenario B>: [critical] item N is X -- <one-line reason for drop>
  - Issue: <what observably happened>
  - Cause: <why, at the instruction level>
  - General Fix Rule: <class-level abstraction>
- <Scenario A>: (nothing new)

### Discretionary fill-ins (newly surfaced this time)
- <Scenario B>: <fill-in content>

### Ledger updates
- Added: <pattern name> (from Scenario B)
- Re-seen: <pattern name> (originally iter K) -- existing fix did not prevent recurrence because <reason>

### Next fix proposal
- <one-line minimum fix>

(Convergence check: X consecutive clears / Y rounds remaining to stop condition)
```

## Red Flags (beware of rationalization)

| Rationalization | Reality |
|---|---|
| "Rereading it myself has the same effect" | Cannot view own text objectively. Always dispatch new subagent. |
| "One scenario is enough" | One scenario overfits. Minimum 2, ideally 3. |
| "Zero unclear points once, so we're done" | Could be coincidence. Finalize with 2 consecutive rounds. |
| "Let's knock out multiple unclear points at once" | Lose track of what worked. One theme per iteration. |
| "Split each micro-fix into its own iter" | Opposite trap. "One theme" is a semantic unit. 2-3 related micro-fixes can bundle. |
| "Metrics are good, so ignore qualitative" | Time reduction can mean too thin. Keep qualitative primary. |
| "Rewriting from scratch is faster" | Correct after 3+ iters of no decrease. Before that, it is escape. |
| "Reuse the same subagent" | It learned previous improvements. Always dispatch new one. |

## Common Failures

- **Scenario too easy/hard**: neither produces signal. One median, one edge.
- **Only looking at metrics**: chasing time reduction strips explanations.
- **Too many changes per iteration**: cannot trace which fix worked.
- **Tuning scenarios to match fix**: making scenario easier to eliminate unclear points is cart-before-horse.
