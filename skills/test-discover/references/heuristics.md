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

## Frontend (React/TS/Next.js)

- Async state rendering: loading -> success, loading -> error, loading -> empty
- Route handling: deep links, query parameter preservation, 404 pages
- Form validation timing: on-blur vs on-submit vs real-time
- Interaction ordering: tab through fields, skip optional fields, back-button mid-flow
- SSR vs CSR: hydration mismatch, client-only features
- Client/server state sync: stale cache, optimistic update rollback

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
