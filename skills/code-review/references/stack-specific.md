# Stack-Specific Review Checklists

## Next.js / React
- Server vs Client component boundary is intentional.
- Data fetching strategy avoids duplicate requests and hydration mismatch.
- `useEffect` dependencies are complete and stable.
- Accessibility and keyboard interactions are preserved.
- Route-level loading/error states are handled.

## TypeScript (General)
- No `any` introduction; explicit types for public boundaries.
- Unsafe type assertions are minimized and justified.
- Union/nullable branches are fully handled.
- Shared types are reused rather than duplicated.

## Node.js Backend
- Input validation exists at API boundaries.
- Async error handling is consistent.
- Timeouts/retries/circuit handling are explicit for external calls.
- Logging avoids secrets and PII leakage.

## Spring Boot
- Transaction boundaries are explicit and correct.
- N+1 query risks are checked for repository/service changes.
- Validation annotations and error responses are consistent.
- Security config changes are reviewed for endpoint exposure.

## Python
- Type hints are present for core interfaces.
- Exception handling is narrow and meaningful.
- Mutable default arguments are avoided.
- I/O and network paths handle timeout and retry behavior.

## Database / Migration
- Migration is backward-compatible for rolling deploy.
- Index/constraint changes are evaluated for lock/runtime impact.
- Backfill strategy and rollback path are defined.
- Query plan or performance risk is acknowledged.

## Infra / CI
- Build/test pipeline impact is explicit.
- Secrets are not hard-coded or leaked in logs.
- New environment variables are documented with scope (`local/dev/test/prod`).
- Rollout and rollback steps are documented.
