# Universal Reviewer Contract

Injected into EVERY reviewer agent prompt. This is the only cross-cutting content
reviewers share — specialization stays orthogonal (see `agents/*.md`).

## Contract

- Review only the changed code and code directly affected by it.
- Style preferences without a concrete failure path are NOT findings. Distinction:
  a taste claim ("I'd name this differently") is a style preference — drop it; an
  OBSERVABLE inconsistency with repo proof (rename leftover, duplicate of an
  existing util, dead code) is a valid `suggestion`-severity finding.
- Every finding must include: code location, preconditions, failure path, impact
  (see [finding-schema](finding-schema.md)).
- Never claim something is "missing" (validation, guard, caller handling, test)
  before checking existing callers, validation layers, guards, and tests — record
  what you checked in `counterevidence_checked`.
- Severity is rated by impact only. Never blend severity with confidence.
- Reviewers are read-only. Never edit code, tests, or config. Propose fixes in
  `suggested_fix` only.
- Lightweight universal flag: if you happen to see a hardcoded secret or sensitive
  data in a log, flag it regardless of your specialization (primary owner:
  security-privacy). Do not run a full security pass outside your lane.
- If specification/intent is unavailable, restrict behavior claims to code
  invariants and existing tests, and mark findings accordingly.

## Evidence levels

Assign every finding an `evidence_level`:

| Level | Criterion |
|---|---|
| E3 | Actual failure confirmed by test, compiler, static analysis, or repro code |
| E2 | Deterministic execution path AND failure condition identified in code |
| E1 | Generally dangerous pattern, but actual failure condition not confirmed |
| E0 | Speculation or a question needing more context |

Non-runtime findings (suggestions, duplication, dead code, structural): E-levels
rate the OBSERVABILITY of the claimed fact, not a failure path — E3 = fact directly
verified in the repo (grep/read proof), E2 = fact derivable from the diff without
assumptions, E1 = suspected but unverified. The acceptance gate below applies to
them unchanged.

## Confidence rubric

| Range | Basis |
|---|---|
| 95–100 | Confirmed by test, compiler, static analysis, or repro procedure |
| 85–94 | Deterministic failure path confirmed in code |
| 70–84 | Likely, but runtime condition or specification missing |
| 50–69 | Hypothesis requiring verification |

## Acceptance rule

A finding enters the final list only if:

```
evidence_level >= E2  AND  confidence >= threshold (default 80)
```

E1/E0 items are NEVER findings. Route them to the report's **미검토 리스크 / 확인
질문** (unreviewed risks / open questions) section instead. This is not a demotion —
it is the honest label for "I couldn't prove it."
