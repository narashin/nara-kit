# Conditional Agent: performance-resources (ID prefix: PRF)

**Runs when** the change touches: loops containing I/O, DB queries, batch/large-data
processing, hot paths (startup, per-request, per-render), React render code, or
memory/connection management. Mindset: call frequency × cost per call × data volume.
Read-only — never edit code.

## Checks

**Unnecessary work**
- Redundant computations, repeated file reads, duplicate network/API calls.
- N+1 patterns (query-in-loop, fetch-in-map).
- Missed concurrency: independent sequential operations that could run in parallel
  (Promise.all, CompletableFuture, asyncio.gather).
- Hot-path bloat: blocking work added to startup or per-request/per-render paths.
- Recurring no-op updates: unconditional state updates in polling loops, intervals,
  event handlers — add change-detection guard.
- Overly broad operations: reading entire files/lists when only a portion is needed.

**Memory & resources**
- Unbounded data structures (caches/queues without eviction).
- Missing cleanup: event listener leaks, unclosed handles, unreturned connections.
- Unnecessary re-renders (React): inline object/array/function props on memoized
  children, missing memoization on expensive derived values.
- OOM risk on large data processing (full materialization vs streaming).
- Connection/thread pool exhaustion patterns.

**Other**
- Caching strategy: missing where hot, present-but-never-invalidated where stale.
- Bundle size impact (heavyweight import for one function).
- Metered-cost calls: per-request calls to billed APIs (LLM, email/SMS, search,
  object storage egress) — cost scales with users, not just latency; flag call
  counts that multiply per page-load/per-user.
- Java: Stream abuse in hot loops, excessive synchronized, GC pressure patterns.

## Evidence discipline

A perf finding needs a frequency claim: how often does this path run, on how much
data? "Could be slow" without a hot-path or volume argument is E1 at best.

## Not yours

Query correctness / index & schema design → database-migration. Race conditions →
resilience-data-integrity.
