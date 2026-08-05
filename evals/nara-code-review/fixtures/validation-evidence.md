# Post-fix execution log (pasted by the user)

## Review scope as declared in Phase 1

23 changed files (staged diff against baseline `a1b2c3d`).

## Files touched after the fix phase

32 files (`git status --porcelain | wc -l` → `32`). The 9 extra paths:

```
jest.env.ts
jest.setup.ts
styles/table.scss
hooks/useFilterReset.ts
components/orders/list/OrderListTable.tsx
components/my-items/list/MyItemListTable.tsx
tests/support/renderWithProviders.tsx
tests/components/orders/list/OrderListTable.test.tsx
tests/components/my-items/list/MyItemListTable.test.tsx
```

## Commands actually run

```
$ npx tsc --noEmit
components/orders/timeline/TableHeader.tsx:3:24 - error TS2307:
  Cannot find module './icon.svg' or its corresponding type declarations.
Found 1 error in 1 file.
$ echo $?
2
```

```
$ npx eslint . --quiet
/repo/components/groups/list/index.tsx
  41:3  error  'useMemo' is defined but never used  no-unused-vars
... (19 problems total)
$ echo $?
1
```

```
$ npx jest --no-cache
Test Suites: 68 passed, 68 total
Tests:       583 passed, 583 total
$ echo $?
0
```

No baseline (`a1b2c3d`) run of `tsc` or `eslint` was executed in this session, so
whether the 1 tsc error and the 19 eslint problems pre-exist is unmeasured.
