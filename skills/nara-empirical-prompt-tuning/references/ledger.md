# EPT Failure Pattern Ledger

Maintain a cumulative list of failure modes across iterations. Without it, each iteration re-discovers the same class of mistake.

## Entry Format

```
- **Pattern name**: short descriptive handle (not "ambiguous X"; prefer "over-eager template application when skip clause is absent")
  - Example: <representative Issue wording from some iter>
  - General Fix Rule: <the class-level rule from that iter's structured reflection>
  - Seen in: iter N, iter M, ...
```

## Rules

- Before generating a fix (Workflow step 5), scan the ledger. If the current `General Fix Rule` matches an existing entry, update `Seen in` and investigate why the existing fix did not prevent recurrence before creating a new entry.
- A pattern that recurs 3+ times despite targeted fixes is a structural signal -- escalate to divergence criterion rather than patching.
- The ledger is per-target-prompt, not global across all EPT runs.
