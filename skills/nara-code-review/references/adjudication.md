# Phase 5: Adjudication — Blind Judge

Reviewers generate suspicion; the Judge decides. An independent Judge agent
re-verifies findings before anything is fixed or reported as confirmed.

## What requires a Judge (mandatory)

- All `critical` / `major` / `minor` findings — a minor claim that is false still
  costs the reader a fix, so severity does not buy a pass on fact-checking
- ALL security-privacy findings (any severity)
- ALL auto-fix candidates (anything the Fixer would touch). Policy-excluded items
  are NOT candidates regardless of mechanical triviality: `suggestion` severity
  (never fixed in any mode) and R3.
- Findings where two reviewers reached conflicting conclusions

Only `suggestion` findings may skip adjudication (never fixed in any mode) — they
are labeled `unadjudicated` in the report.

## Blindness rules

The Judge receives: location, invariant, preconditions, failure_path, evidence,
counterevidence_checked, the diff, and full file context.

For `FID` (spec-fidelity) findings the Judge also receives the cited requirement
section itself, not just the quote — the fact to check is whether the quote is real,
in scope of this change, and actually contradicted by the code.

The Judge must NOT receive:

- the original reviewer's `confidence`
- the `suggested_fix`
- whether other agents found the same issue (reporter overlap)

These anchor the Judge toward the reviewer's conclusion. The Judge independently
re-walks the failure path in the actual code and actively looks for counterevidence
the reviewer missed (existing guards, callers, tests).

## Rejection bar

A finding is `rejected` only on **direct contradictory evidence** the Judge found in
the code: a covering guard, an invariant that makes the state impossible, a caller or
validation layer that already handles it, a test or runtime witness, or proof the
behavior is unchanged. "Looks speculative", a low confidence score, or another
reviewer's clean result is not a rejection reason. `reason` quotes the contradicting
location.

When the Judge can neither re-derive the failure path nor contradict it, the verdict
is `needs-context`. `downgraded` is for impact the Judge measured to be smaller
(narrower blast radius, recoverable) — never a way to encode doubt.

## Implementer claims (leads, not evidence)

The context map's **claimed** bundle ([context-map](context-map.md) 2b) — reasons,
"already handled by X", "tested" — reaches the Judge and never the reviewers. Each
claim is a lead to check in code. One that checks out becomes contradictory evidence
under the bar above; one that does not is ignored. Never reject because the
implementer said so.

A `FID` finding marked `declared: <entry>` is not a candidate for rejection on that
ground either: the deviation being intentional is why it is R3, not why it is wrong.
The Judge checks only that the quoted spec and the quoted entry are real and that the
code matches the entry; the verdict stays `confirmed` at R3 for a human to decide.

## Judge output

```yaml
finding_id: BEH-001
verdict: confirmed | rejected | downgraded | needs-context
reason: >-
  ...
verified_failure_path: >-      # the Judge's OWN re-derivation, not a copy
  ...
missing_context: ...           # only for needs-context
final_severity: critical | major | minor | suggestion
final_confidence: 0-100        # Judge's own rubric score (reviewer-contract.md)
```

## Verdict handling

| Verdict | Effect |
|---|---|
| confirmed | Enters issue ledger with final_severity/final_confidence |
| downgraded | Enters ledger at the lower severity; excluded from auto-fix if now below gate |
| rejected | Report's SKIP section with the Judge's reason |
| needs-context | Report's 확인 질문 (open questions) — never fixed, never counted as a defect |
| disproved | Rebuttal outcome only (below) — Report's SKIP section with the counter-evidence |

Only `confirmed` (and `downgraded` still meeting the acceptance gate) findings reach
the Fixer. The Judge never edits code.

## Rebuttal without a code change

When the Fixer or the user holds concrete counter-evidence against a `confirmed`
finding, the answer is neither an empty fix nor a quiet skip. Send the original
finding plus the cited guard, invariant, contract, or test output to a **fresh**
Judge (not the one that confirmed it), which checks only that finding.

- Accepted → `disproved`, closed with the Judge's own contradictory evidence.
- Not accepted, or undecidable → the finding stays open and returns to the normal
  fix flow with the reason.
- Preference or a bare denial does not qualify. The Fixer and the main session
  cannot dismiss a finding themselves.
- Once per finding per reviewed state. It does not restart discovery and does not
  consume a round by itself; it runs inside the current round, before that round's
  fixes are applied, and the ledger entry becomes `DISPROVED`
  ([verification](verification.md)).
