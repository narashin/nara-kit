# Stack-Specific Review Checks

Additional checks per tech stack. After identifying the stack, apply the relevant section alongside the main 5-agent review.

---

## Next.js + React (TypeScript)

### Routing & Rendering
- [ ] App Router vs Pages Router mixing issues
- [ ] Server Component vs Client Component separation (`'use client'` missing or unnecessary)
- [ ] Proper use of `generateStaticParams`, `generateMetadata`
- [ ] Dynamic route parameter validation
- [ ] Middleware redirect/rewrite logic correctness

### Data Fetching
- [ ] Error handling in Server Actions
- [ ] Proper `revalidatePath` / `revalidateTag` usage
- [ ] TanStack Query queryKey uniqueness and cache invalidation strategy
- [ ] Unnecessary client-side fetching (data available server-side)
- [ ] `Suspense` boundary placement appropriateness

### Forms & State
- [ ] React Hook Form `reset`, `setValue` re-render optimization
- [ ] Optimistic update handling on form submission
- [ ] Proper `useFormState` / `useActionState` usage
- [ ] Controlled/uncontrolled component mixing

### Performance
- [ ] `Image` component usage (instead of raw `<img>`)
- [ ] `dynamic(() => import(...))` lazy loading
- [ ] Missing or index-based `key` prop
- [ ] Context splitting (avoid single giant context)

---

## Node.js Backend

### API Design
- [ ] RESTful conventions (HTTP methods, status codes)
- [ ] Input validation middleware (zod, joi, etc.)
- [ ] Response format consistency (envelope pattern)
- [ ] API versioning strategy

### Database
- [ ] ORM N+1 issues (eager loading needed?)
- [ ] Migration rollback capability
- [ ] Index usage for large dataset queries
- [ ] Connection pool management
- [ ] Transaction isolation level appropriateness

### Security
- [ ] CORS configuration
- [ ] Rate limiting
- [ ] JWT validation and expiry handling
- [ ] Secrets managed via environment variables

---

## Java (Spring Boot / General)

### Object Design & Patterns
- [ ] SOLID compliance (especially SRP, DIP)
- [ ] Immutable objects (record, final fields, defensive copies)
- [ ] Appropriate Builder / Factory pattern usage
- [ ] Composition over inheritance
- [ ] DTO ↔ Entity conversion layer separation
- [ ] equals / hashCode contract (especially JPA entities)

### Type & Null Safety
- [ ] Correct Optional usage (avoid as fields, use for return types)
- [ ] `@Nullable` / `@NonNull` annotations
- [ ] NullPointerException risk points
- [ ] Generic wildcard (`? extends`, `? super`) appropriateness
- [ ] Raw type avoidance

### Spring-Specific
- [ ] Bean scope correctness (no mutable state in singletons)
- [ ] `@Transactional` scope and propagation settings
- [ ] `@Transactional(readOnly=true)` on read-only methods
- [ ] Circular dependency detection
- [ ] `@Async` proxy self-invocation issue
- [ ] Exception handler hierarchy (`@ControllerAdvice`)
- [ ] Profile-based config separation (dev / staging / prod)

### Concurrency & Thread Safety
- [ ] Synchronization on shared mutable state
- [ ] `ConcurrentHashMap`, `AtomicReference` usage
- [ ] Deadlock risk (lock ordering consistency)
- [ ] `@Async` / `CompletableFuture` error handling
- [ ] Thread pool sizing appropriateness

### JPA & Database
- [ ] `LazyInitializationException` risk
- [ ] Fetch join vs EntityGraph for N+1 prevention
- [ ] Persistence context `clear()` after bulk operations
- [ ] Optimistic lock (`@Version`) / pessimistic lock strategy
- [ ] JPQL/QueryDSL parameter binding (SQL injection prevention)
- [ ] Index hints and query plan considerations

### Performance
- [ ] Stream API overuse (simple loop would be better)
- [ ] Unnecessary boxing/unboxing (Integer ↔ int)
- [ ] StringBuilder for string concatenation in loops
- [ ] Connection pool / thread pool resource leaks
- [ ] GC-heavy object creation patterns

---

## Python (CLI / Scripts)

### Code Quality
- [ ] Type hints (mypy compatible)
- [ ] `__main__` block separation
- [ ] Specific exception classes (avoid generic Exception)
- [ ] Context manager (`with`) for resource management

### CLI Tools
- [ ] argparse / click / typer help text completeness
- [ ] Proper exit code returns
- [ ] stdin/stdout/stderr separation
- [ ] Signal handling (Ctrl+C graceful shutdown)

### Dependencies
- [ ] requirements.txt / pyproject.toml consistency
- [ ] Virtual environment isolation
- [ ] Minimum Python version specified

---

## Common (All Stacks)

### Git & Collaboration
- [ ] Commit message convention compliance
- [ ] Change scope is a single logical unit
- [ ] No leftover debug artifacts (console.log, print, etc.)

### Testing
- [ ] Tests exist for changed logic
- [ ] Edge case test coverage
- [ ] Test isolation (no inter-test dependencies)
- [ ] Appropriate mocking (not so much that tests become meaningless)

### Documentation
- [ ] Comments on complex logic (explaining *why*, not *what*)
- [ ] JSDoc / docstring for public APIs
- [ ] README or wiki update needed?
