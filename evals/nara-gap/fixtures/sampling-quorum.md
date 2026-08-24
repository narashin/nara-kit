# docs/requirements.md (excerpt)

- [ ] FR-1: The list should paginate at 20 rows per page.
- [ ] FR-2: The list should sort by `updatedAt` descending by default.
- [ ] FR-3: The list should offer a `Clear` button that resets every filter.
- [ ] FR-4: The list should keep the filter state in the query string.
- [ ] FR-5: The empty state should read `No results found`.
- [ ] FR-6: The row count label should read `{n} items`.
- [ ] FR-7: The list should debounce the search input by 300ms.
- [ ] FR-8: The list should show a skeleton row while loading.
- [ ] FR-9: The detail link should open in the same tab.
- [ ] FR-10: The list should retain scroll position on back navigation.

# docs/gap.md (existing — produced by a previous run, whose Needs Confirm items the user already answered)

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: 2026-07-02
- Score: 80/100
- **Gate: ⚠️ score 80 (P1 보완 권장)**

## Summary
- Total: 10 | Implemented: 8 | Partial: 0 | Missing: 0 | Agreed Exception: 0
- **P0 Missing (Critical): 0**
- Needs Confirm: 2 (forced sampling)

## Detail

### Implemented
| ID | Priority | Requirement | Quote | Evidence (파일:라인) | Verbatim? |
|---|---|---|---|---|---|
| FR-1 | P1 | paginate at 20 | "20 rows per page" | src/list/pagination.ts:12 | N |
| FR-2 | P1 | default sort | `updatedAt` | src/list/sort.ts:14 | Y |
| FR-3 | P0 | Clear resets filters | `Clear` | src/list/Toolbar.tsx:38 | Y |
| FR-4 | P1 | filter state in query | "query string" | src/list/useFilterQuery.ts:19 | N |
| FR-5 | P0 | empty state copy | `No results found` | src/list/EmptyState.tsx:9 | Y |
| FR-6 | P0 | row count label | `{n} items` | src/list/CountLabel.tsx:11 | Y |
| FR-7 | P1 | debounce 300ms | "300ms" | src/list/useSearch.ts:27 | N |
| FR-8 | P1 | skeleton while loading | "skeleton row" | src/list/Skeleton.tsx:6 | N |

### Needs Confirm (forced sampling — user 확인 요청)
| ID | Priority | Requirement | Why sampled | Evidence |
|---|---|---|---|---|
| FR-9 | P1 | detail link same tab | verbatim | src/list/Row.tsx:41 |
| FR-10 | P1 | retain scroll position | short evidence | src/list/useScroll.ts:8 |
```

# Workspace state (raw command output — no interpretation supplied)

```
$ wc -l src/list/*.ts src/list/*.tsx
      88 src/list/pagination.ts
      31 src/list/sort.ts
      54 src/list/useFilterQuery.ts
      40 src/list/useSearch.ts
      22 src/list/useScroll.ts
      60 src/list/Toolbar.tsx
      18 src/list/EmptyState.tsx
      25 src/list/CountLabel.tsx
      14 src/list/Skeleton.tsx
      70 src/list/Row.tsx
     422 total
```

```
$ git grep -Fn "Clear" src/list/Toolbar.tsx
src/list/Toolbar.tsx:38:      <Button onClick={resetAll}>Clear</Button>
```

```
$ git grep -Fn "No results found" src/list/EmptyState.tsx
src/list/EmptyState.tsx:9:  return <p>No results found</p>
```

```
$ git grep -Fn "{n} items" src/list
src/list/CountLabel.tsx:11:  return <span>{`${n} items`}</span>
```

Every path cited in `docs/gap.md` exists and every cited line number is within
the file's line count. No external-repository citations appear in `docs/gap.md`.
No `docs/implementation-notes.md` in this workspace.
