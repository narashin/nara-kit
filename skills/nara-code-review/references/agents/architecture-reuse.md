# Conditional Agent: architecture-reuse (ID prefix: ARC)

**Runs when** the change adds a new module/abstraction/dependency, touches multiple
layers, or duplicates common code. Read-only — never edit code.

## Checks

**Code reuse (top priority)**
- Search if similar utilities/helpers/components already exist in the project —
  scan utility directories, shared modules, adjacent files.
- Detect inline logic replaceable by existing utils: hand-rolled string manipulation,
  manual path handling, custom env checks, ad-hoc type guards.
- Reinventing existing components: new component/function duplicating existing
  functionality — suggest the existing one.

**Design quality**
- Consistency with existing code patterns/conventions; new code diverging from
  surrounding patterns without justification.
- Dependency direction (circular dependency detection).
- Separation of concerns (SRP violations).
- Over-abstraction / over-engineering.
- File/folder structure convention violations.
- Magic numbers: numeric literals that should be named constants (thresholds,
  timeouts, limits, IDs, indices).
- Constants/defaults that contradict each other across code and config.
- `as const` overuse: no narrowing benefit, or narrowed literal type never consumed.

**Hacky pattern detection**
- Redundant state: state duplicating existing state, cached values derivable from
  other state, observers/effects that could be direct calls.
- Parameter sprawl: adding parameters instead of generalizing/restructuring.
- Copy-paste with slight variation: near-duplicate blocks that should be unified.
- Leaky abstractions: exposing internals or breaking existing abstraction boundaries.
- Add-without-delete: new code path added while the old path it replaces stays
  alive with no removal plan — both must be maintained forever.
- Temporary compatibility code (shims, dual-write, legacy branches) without an
  explicit removal condition or date.

**Stack-specific**
- Spring: Bean scope misuse, circular dependencies.
- React: component split granularity, props drilling vs context.

## Structural lens (report-only, auto-detected)

Trigger — only when review scope spans multiple commits or a pre-refactor intent is
detected (not a flag). Otherwise skip.

- Surface recurring cross-file coupling / boundary leaks / ownership confusion as
  **candidates** (accumulated friction, not single-diff defects).
- **Report-only** — structural findings are `fix_risk: R3` fixed (never auto-fixed;
  no refactor/rename/move execution).
- Anti-claim: never claim a structural problem "solved" by writing a report/doc.
- Each structural finding's `suggested_fix` must contain the smallest-safe-next-step
  — no big-bang rewrite proposals. Final call is human.

## Not yours

Type duplication → contracts-compatibility. Dockerfile/Helm/README alignment →
operations-config. Design-token conformance → frontend-ux-a11y.
