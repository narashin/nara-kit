# Test Scenario Heuristic Catalog

## Universal (apply to all targets)

- Empty/null/undefined values
- Boundary values (0, -1, max, max+1, empty string, single char, max-length string)
- Type boundaries (integer overflow, float precision, unicode/emoji)
- State-dependent behavior (action in wrong state, repeated action, action after timeout)
- Concurrency (simultaneous requests, double-click, rapid sequential calls)
- External dependency failure (network down, service timeout, malformed response)
- Idempotency (same action twice -> same result?)
- Large input / timeout (payload size limits, pagination boundaries)
- **Acceptance invariant (positive direction)**: a fully-valid input combination MUST be accepted/processed — not just "invalid input is rejected". For every "invalid -> rejected" candidate, pair a "valid -> accepted + completes". Systems that silently refuse valid input (stuck submit, unsatisfiable conditional rule) are invisible to rejection-only tests.
- **Cross-field / stateful validation corruption**: mutating one field/param must not corrupt another field's validity. After each state-mutating op, re-supply a valid combination and assert it is still accepted. Applies to UI forms (re-register/reset), conditional cross-field rules (field A flips an unsatisfiable required on field B), and multi-step state machines.
- **Value-parametrized acceptance**: for enum/option fields, iterate ALL values -> combine with otherwise-valid input -> assert accepted for each. The specific corrupting value is emergent (surfaces at runtime); discovery emits the parametrization, execution is the detector.

## Frontend (React/TS/Next.js)

- Async state rendering: loading -> success, loading -> error, loading -> empty
- Route handling: deep links, query parameter preservation, 404 pages
- Form validation timing: on-blur vs on-submit vs real-time
- Interaction ordering: tab through fields, skip optional fields, back-button mid-flow
- SSR vs CSR: hydration mismatch, client-only features
- Client/server state sync: stale cache, optimistic update rollback
- Form submittability (React impl of Universal "Acceptance invariant" + "Cross-field corruption"): render the ASSEMBLED form (real form lib + real submit, async children mocked), fill all-valid -> submit fires with complete payload + zero error nodes. Then after each state-mutating op (`reset()`/import, `resetField()`, field re-register, toggle ON->OFF) re-enter valid -> assert errors clear AND submit proceeds. Per-field isolated tests are structurally blind to this. (Concrete bug class: useCallback stale closure / RHF re-register on reset corrupts a sibling field's validator -> valid form can't submit.)

## Backend (Java/Python/TS)

- HTTP status codes: 200/201/204/400/401/403/404/409/422/500
- Auth/authz: missing token, expired token, insufficient permissions, role escalation
- Transaction boundaries: partial failure, rollback behavior
- DB constraint violations: unique, foreign key, not-null, check constraints
- Pagination/filter: first page, last page, empty result, invalid page number
- Serialization/timezone: date format, UTC vs local, DST transitions
- Race conditions: concurrent writes, optimistic locking conflicts
- API contract: required fields missing, extra fields, wrong types

## E2E (web)

- Deep link: direct URL entry restores full page state
- Refresh: F5 preserves current view/data
- Navigation: back/forward buttons, breadcrumb, sidebar
- Multi-tab: same page in two tabs, action in one reflects in other
- Toast/modal: appears on action, disappears on timeout, blocks interaction when modal
- Network latency: slow response shows loading, timeout shows error
