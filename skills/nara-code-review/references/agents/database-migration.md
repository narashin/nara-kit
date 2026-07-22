# Conditional Agent: database-migration (ID prefix: DBM)

**Runs when** the change touches: schema/migration files, entities, repositories,
or query code. Read-only — never edit code.

## Checks

**Schema & migration safety**
- Migration rollback capability (down migration exists and actually reverses).
- Destructive migration (DROP/rename column, type narrowing) without backfill or
  deploy-order plan — old code must survive against new schema during rollout.
- Long-lock risk: ALTER on large tables, missing online-migration strategy where
  the project has one.
- Default values / NOT NULL added to existing columns — behavior on existing rows.
- Data backfill: idempotent, batched, resumable for large tables.

**Query correctness & performance**
- Missing index for new query patterns; full table scan risk.
- ORM N+1 (eager loading needed?); fetch join vs EntityGraph (JPA).
- Query returning unbounded result sets (missing pagination/limit).
- JPQL/QueryDSL/raw SQL parameter binding (injection prevention — coordinate with
  security-privacy; own the query-shape aspect).

**Entity & mapping**
- JPA: LazyInitializationException risk, equals/hashCode contract on entities,
  persistence context clear() after bulk operations.
- Optimistic (`@Version`) / pessimistic lock strategy matching the concurrency
  pattern of the change.
- Entity type ↔ column type precision mismatches (coordinate with
  contracts-compatibility; own the schema side).
- Transaction isolation level appropriateness for the new access pattern.

**Operational**
- Connection pool sizing vs new query volume.
- Migration files ordering/naming per project convention; checksum-stable edits
  (never editing an applied migration).

## Not yours

Transaction rollback in application code → resilience-data-integrity. General perf
outside DB → performance-resources.
