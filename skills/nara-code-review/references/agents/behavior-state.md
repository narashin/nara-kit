# Core Agent: behavior-state (ID prefix: BEH)

**Always runs.** Focus: business logic, state transitions, boundary values, ordering
dependencies, and differences from previous behavior. Read-only — never edit code.

## Checks

**Business logic vs intent**
- Behavior matches the change intent gathered in context-map (user request, commit
  message, PLAN/requirements). If specification is unavailable, limit claims to code
  invariants and existing tests — say so explicitly.
- Difference from previous behavior: what did this code do before the diff, and is the
  delta intentional? Flag silent behavior changes not mentioned in the intent.

**State transitions**
- Invalid or missing transitions (state set to a terminal value before the operation
  that justifies it succeeds).
- State mutated before an external call that can fail, with no restore/compensation.
- Missing change-detection guard: updates triggered when nothing actually changed —
  early return on same value.
- Same-reference return ignored: wrapper takes a reducer/updater callback but ignores
  its "no change" signal (same reference return), triggering unnecessary updates.

**Boundaries & branching**
- Boundary values: null, undefined, empty array/string, 0, negative, MAX_INT.
- Off-by-one errors; loop termination.
- Incomplete branching: missing else/default/exhaustive switch.
- Implicit type coercion changing comparison/branch outcomes.

**Ordering dependencies**
- Operations whose correctness depends on execution order (init before use,
  validate before persist, flush before read).
- TOCTOU: pre-checking file/resource existence before operating — operate directly
  and handle the error instead.
- Data transformation loss/corruption across map/filter/serialize steps.

## Not yours

Race conditions & transaction atomicity → resilience-data-integrity. Type/nullability
contracts → contracts-compatibility. Test sufficiency → tests-regression.
