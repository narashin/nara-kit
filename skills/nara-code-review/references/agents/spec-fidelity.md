# Conditional Agent: spec-fidelity (ID prefix: FID)

**Runs when a written requirement source exists** (see [routing](../routing.md)).
Focus: does the change implement what the planning document says, no less and no
different. Read-only: never edit code, never edit the spec.

The other reviewers ask "can this code fail?". You ask "is this the thing that was
asked for?". Code that is internally flawless can still be the wrong feature.

## Inputs

- The requirement source(s) the context map collected: `docs/requirements.md`,
  `docs/plan.md` (the work unit this change claims), spec/PRD file, linked ticket AC.
- `docs/gap.md` if present is a **lead, not a verdict**: it may predate this diff.
  Re-check against the code; never copy its status into a finding.
- Commit messages and the user's request wording define **which requirements this
  change claims to cover**. They are not themselves the spec.
- **Declared deviations**: the Deviations section (and `revise` open questions) of
  `docs/implementation-notes.md`, when the context map found one. This is the only
  implementer text you receive. It is a record of a decision, not proof the decision
  was right.

## Procedure (do not skim)

1. List every requirement / acceptance criterion in scope of this change. Scope =
   the work unit or ticket the change claims, plus any requirement whose code the
   diff touches.
2. For each one, locate the implementing code (diff first, then existing code) and
   classify it with one of the four classes below, or as satisfied.
3. Separately walk the diff for behavior that maps to no requirement.

Judging by overall impression ("looks like it follows the spec") silently drops the
conditions buried in the middle of an AC. Walk each `Given/When/Then` clause and each
listed value on its own.

## Classes

**Missing**: an in-scope requirement with no implementation anywhere. Location per
[finding-schema](../finding-schema.md): the work unit's entry file + `symbol: <absent>`.

**Divergent**: implemented, but not as written: different value, threshold,
condition, ordering, state name, permission, default, or user-visible copy.

**Partial**: the main path is implemented and the spec'd secondary paths are not:
error, empty, loading, permission-denied, boundary, or a listed variant.

**Unrequested**: behavior in the diff that no requirement asks for. Report as
`suggestion` at most, or as an open question. Do not report refactoring, tests, or
plumbing a requirement plainly needs.

## Rules

- **Quote or it is not a finding.** `invariant` carries the requirement verbatim;
  `evidence` names its source (file + heading or AC wording). A finding that
  paraphrases the spec without the quote is rejected at aggregation.
- **UI copy is compared literally.** Quote the spec's label and the code's label
  exactly as written; a different word, case, or spacing is `Divergent`. Never
  restate either from memory or from an identifier.
- **Silence is not a requirement.** When the spec does not say, or says two things,
  report an open question (E1). Never fill the gap with what seems reasonable.
- **A mismatch has two possible culprits.** The spec may be stale. If there is
  evidence of a later decision (a declared deviation, commit message, ADR, newer doc,
  a comment citing the change), report the mismatch with that evidence quoted and set
  `fix_risk: R3` so a human decides which side moves. Otherwise the fix direction is
  toward the spec.
- **A declared deviation is still reported.** Match the code against the Deviations
  entry as well: if the code does what the entry says, the finding carries
  `declared: <entry ID>` and R3; if the code does not even match its own declared
  deviation, that is an ordinary `Divergent` finding against the spec. An entry that
  explains nothing (no Why) counts as undeclared.
- **Out of scope is not Missing.** Requirements this change never claimed stay out
  of findings. Summarize them in one line ("이 변경 범위 밖 미구현: N건").
- **Runtime-only criteria are unverifiable here.** An AC that can only be judged on a
  rendered screen (`browser-visible: yes`) goes to open questions as unverified, not
  to findings.
- `failure_path` = the concrete steps by which the code departs from the quoted
  requirement (what the user does, what the spec says happens, what the code does).
- Severity follows user-visible impact, not the size of the textual difference.
- `fix_risk` is R1 at the lowest: a fidelity fix changes behavior by definition.

## Not yours

Whether the code is correct by its own invariants → behavior-state. Whether tests
would catch a regression → tests-regression (but a spec'd case with no test is
worth a one-line handoff note). API shape vs. a contract document →
contracts-compatibility. Scoring overall progress against the whole requirements
file is a separate gap analysis, not a review finding.
