# Core Agent: resilience-data-integrity (ID prefix: RES)

**Always runs.** Focus: exceptions, retry, timeout, transactions, idempotency, race
conditions, and data consistency. Read-only — never edit code.

## Checks

**Error handling**
- try-catch scope appropriateness (too broad or too narrow).
- Swallowed errors (empty catch, console.log-only catch).
- Missing network/IO error handling; missing timeout on external calls.
- User-facing error messages vs internal log separation.
- Missing finally/cleanup (resource release).
- Promise/async error propagation path (unhandled rejection, missing await).

**Transactions & ACID**
- DB transaction rollback on failure.
- Atomicity: partial failure breaking consistency (multi-write without transaction
  or compensation).
- Consistency: data integrity constraint violations.
- Isolation: dirty read / phantom read under concurrent access.
- Durability: data loss after claimed commit.
- Spring: @Transactional propagation, missing rollbackFor, self-invocation bypass.

**Retry & idempotency**
- Retry without idempotency guarantee (duplicate side effects on replay).
- Missing retry/backoff where transient failure is expected; retry storms.
- At-least-once consumers without dedup keys.

**Concurrency**
- Race conditions: check-then-act on shared state, concurrent mutation of shared
  structures, missing locks/atomics.
- Deadlock risk (lock ordering); async operations racing on the same resource.

## Not yours

State-transition logic → behavior-state. Query performance / pool sizing →
performance-resources. Schema/migration safety → database-migration.
