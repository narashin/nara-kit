# docs/requirements.md (excerpt)

- [ ] FR-1: The list view should paginate at 20 rows per page.
- [ ] FR-2: The list view should support sorting by the `updatedAt` column.
- [ ] FR-3: The list view should support filtering by owner.

# docs/gap.md (existing — produced by a previous run)

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: 2026-07-02
- Score: 100/100
- **Gate: ✅ review-ready**

## Summary
- Total: 3 | Implemented: 3 | Partial: 0 | Missing: 0 | Agreed Exception: 0
- **P0 Missing (Critical): 0**
- Needs Confirm: 0 (forced sampling)

## Detail

### Implemented
| ID | Priority | Requirement | Quote | Evidence (파일:라인) | Verbatim? |
|---|---|---|---|---|---|
| FR-1 | P1 | paginate at 20 rows | "20 rows per page" | src/list/pagination.ts:12 | N |
| FR-2 | P1 | sort by updatedAt | `updatedAt` | src/list/sort.ts:400 | Y |
| FR-3 | P1 | filter by owner | "filtering by owner" | src/list/removed-filter.ts:7 | N |
```

# Workspace state (raw command output — no interpretation supplied)

```
$ git ls-files src/list
src/list/pagination.ts
src/list/sort.ts
```

```
$ wc -l src/list/pagination.ts src/list/sort.ts
      88 src/list/pagination.ts
      31 src/list/sort.ts
     119 total
```

```
$ git grep -Fn "updatedAt" src/list
src/list/sort.ts:14:const SORT_KEYS = ['updatedAt', 'name'] as const
```

```
$ git grep -Fn "20" src/list/pagination.ts
src/list/pagination.ts:12:export const PAGE_SIZE = 20
```

No `docs/implementation-notes.md` in this workspace.
