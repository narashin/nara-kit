# Phase 3: 5 Review Agents

**Use the Agent tool to launch all 5 agents concurrently in a single message.**
Pass each agent the full diff and gathered context.

All agents output findings in this format:

```json
{
  "reviewer": "agent-id",
  "severity": "critical | warning | suggestion",
  "confidence": 0-100,
  "file": "filepath",
  "line_range": "start-end",
  "title": "issue title",
  "description": "why this is a problem",
  "impact": "possible incident scenario",
  "suggestion": "concrete fix code",
  "auto_fixable": true | false
}
```

**Confidence rules**: 80+ only for defects directly verifiable in code. Speculative concerns stay at 50 or below.

---

## Agent 1: Logic & Edge Case Analyst (reviewer: "logic")

Focus: **logical errors and missing edge cases only.**

Check for:
- Business logic matches commit intent
- Boundary values: null, undefined, empty array/string, 0, negative, MAX_INT
- Off-by-one errors
- Incomplete branching (missing else/default/exhaustive switch)
- Async race conditions
- Loop termination
- Data transformation loss/corruption
- Implicit type coercion
- **Cross-layer type precision**: DB column type vs ORM type vs application logic (e.g., MySQL `DATETIME` second precision vs Python `datetime` microsecond — equality comparison may silently fail)
- **TOCTOU**: pre-checking file/resource existence before operating — should operate directly and handle the error instead
- **Missing change-detection guard**: triggering updates when nothing actually changed — add early return on same value

---

## Agent 2: Type Safety & Runtime Error Hunter (reviewer: "type-safety")

Focus: **type issues that will crash at runtime.**

Check for:
- TypeScript: `any` abuse, unsafe `as` assertions, missing optional chaining
- Java: NullPointerException risks, raw types, boxing/unboxing hazards
- Python: unexpected dynamic type conversions
- API response type vs actual usage type mismatch
- Unhandled parse failures (JSON.parse, parseInt, etc.)
- Array/object access without existence check
- Incomplete union/enum handling (missing exhaustive check)
- Generic type parameter misuse
- **Stringly-typed code**: using raw strings where constants, enums, string unions, or branded types already exist in the codebase

---

## Agent 3: Error Handling & Resilience Auditor (reviewer: "error-handling")

Focus: **graceful error handling verification.**

Check for:
- try-catch scope appropriateness (too broad or too narrow)
- Swallowed errors (empty catch, console.log-only catch)
- Missing network/IO error handling
- DB transaction rollback on failure
- ACID violations:
  - Atomicity: partial failure breaks consistency
  - Consistency: data integrity constraint violations
  - Isolation: dirty read / phantom read under concurrent access
  - Durability: data loss after commit
- Retry logic necessity (idempotency guarantee)
- User-facing error messages vs internal log separation
- Missing finally/cleanup (resource release)
- Spring: @Transactional propagation, missing rollbackFor
- Promise/async error propagation path
- **Same-reference return ignored**: wrapper function takes reducer/updater callback but ignores the callback's "no change" signal (same reference return), triggering unnecessary updates

---

## Agent 4: Architecture & Compatibility Guardian (reviewer: "architecture")

Focus: **codebase compatibility and design quality.**

**Code Reuse (top priority)**:
- Search if similar utilities/helpers/components already exist in the project
- Scan utility directories, shared modules, adjacent files
- Detect inline logic replaceable by existing utils: hand-rolled string manipulation, manual path handling, custom env checks, ad-hoc type guards
- Flag new functions that duplicate existing functionality — suggest the existing one

**Design Quality**:
- Consistency with existing code patterns/conventions
- Dependency direction (circular dependency detection)
- Separation of concerns (SRP violations)
- API contract changes breaking backward compatibility
- Over-abstraction / over-engineering
- File/folder structure convention violations

**Hacky Pattern Detection**:
- Redundant state: state duplicating existing state, cached values derivable from other state, observers/effects that could be direct calls
- Parameter sprawl: adding parameters instead of generalizing/restructuring
- Copy-paste with slight variation: near-duplicate blocks that should be unified
- Leaky abstractions: exposing internals or breaking existing abstraction boundaries
- Unnecessary JSX nesting: wrapper elements adding no layout value — check if inner component props already handle it

**Infra & Documentation Consistency**:
- Dockerfile: directories created by `mkdir` must match paths actually used in application code (env var defaults, config output dirs)
- README/docs: architecture descriptions (directory structure, file patterns, import paths) must match actual code behavior — flag outdated or unimplemented designs documented as current
- Helm/K8s: env vars in values.yaml must correspond to `os.getenv()` calls in code; port numbers must match `EXPOSE` and listen addresses
- .gitignore: must not exclude files that are tracked and needed (or vice versa)

**Design Consistency (conditional — only when DESIGN.md context is provided)**:
- Hardcoded hex values that should use Tailwind color tokens defined in DESIGN.md
- Border radius values deviating from the project's radius scale (e.g., `rounded-lg` when spec says `{rounded.200}`)
- Font weight usage violating the project's weight mapping (e.g., raw `font-bold` when LDS classes required)
- Color usage violating Do's/Don'ts (e.g., primary color used as content area background)
- Shadow usage on elements where DESIGN.md specifies border-only depth
- Components not using the project's design system library when one is available
- Spacing values outside the defined scale
- Skip this entire section if no DESIGN.md context was provided in Phase 2

**Stack-specific**:
- Spring: Bean scope misuse, circular dependencies
- React: component split granularity, props drilling vs context

---

## Agent 5: Security & Performance Sentinel (reviewer: "security-performance")

Focus: **security vulnerabilities and performance bottlenecks.**

**Security**:
- Injection attacks: SQL Injection, XSS, CSRF, Command Injection
- Missing auth/authorization on API endpoints
- Sensitive data exposure (logs, error messages, hardcoded secrets)
- Missing input validation/sanitization

**Authorization consistency (cross-layer)** — when a change alters server-side permission/capability semantics:
- **Single source of truth**: every consuming layer (client gating, other services) must derive authorization from the SAME server signal. Flag client-side recomputation of permissions that can diverge from the server guard.
- **Overloaded capability flag**: one boolean gating multiple actions whose server rules differ (e.g., edit vs delete) — recommend splitting into per-action flags mapped 1:1 to each backend guard.
- **Unreferenced destructive control**: a component/branch rendering a destructive action but never imported/reached — flag as footgun (auth bypass if later wired) and recommend removal or correct gating.
- **One-sided permission tests**: a permission change tested only at the server guard (or only at the client) — require both the server-guard test and the consuming-layer gating test.

**Performance — Unnecessary Work**:
- Redundant computations, repeated file reads, duplicate network/API calls, N+1 patterns
- **Missed concurrency**: independent sequential operations that could run in parallel (Promise.all, CompletableFuture, etc.)
- **Hot-path bloat**: blocking work added to startup or per-request/per-render hot paths
- **Recurring no-op updates**: unconditional state updates in polling loops, intervals, event handlers — add change-detection guard
- **Overly broad operations**: reading entire files/lists when only a portion is needed

**Memory**:
- Unbounded data structures, missing cleanup, event listener leaks, unreturned connections
- Unnecessary re-renders (React)
- OOM risk on large data processing

**Other**:
- Caching strategy appropriateness
- Bundle size impact
- Java: Stream abuse, excessive synchronized, GC pressure patterns
- DB: missing index usage, full table scan risk
