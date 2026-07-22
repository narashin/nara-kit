# Phase 5: Adjudication — Blind Judge

Reviewers generate suspicion; the Judge decides. An independent Judge agent
re-verifies findings before anything is fixed or reported as confirmed.

## What requires a Judge (mandatory)

- All `critical` / `major` findings
- ALL security-privacy findings (any severity)
- ALL auto-fix candidates (anything the Fixer would touch)
- Findings where two reviewers reached conflicting conclusions

`minor`/`suggestion` findings that will not be auto-fixed may skip adjudication
(cheaper) — they are labeled `unadjudicated` in the report.

## Blindness rules

The Judge receives: location, invariant, preconditions, failure_path, evidence,
counterevidence_checked, the diff, and full file context.

The Judge must NOT receive:

- the original reviewer's `confidence`
- the `suggested_fix`
- whether other agents found the same issue (reporter overlap)

These anchor the Judge toward the reviewer's conclusion. The Judge independently
re-walks the failure path in the actual code and actively looks for counterevidence
the reviewer missed (existing guards, callers, tests).

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

Only `confirmed` (and `downgraded` still meeting the acceptance gate) findings reach
the Fixer. The Judge never edits code.
