# docs/requirements.md (excerpt)

- [ ] FR-1: The download filename must be `report-{date}.csv`.
- [ ] FR-2: The export dialog title must read `Export selection`.
- [ ] FR-3: The export button should be disabled while a job is running.
- [ ] FR-4: The export menu should sit in the toolbar overflow.

# docs/gap.md (existing — produced by a previous run)

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: 2026-07-05
- Score: 25/100
- **Gate: ❌ blocked by P0 (1건)**

## Summary
- Total: 4 | Implemented: 1 | Partial: 0 | Missing: 3 | Agreed Exception: 0
- **P0 Missing (Critical): 1**
- Needs Confirm: 0 (정족수 0 — §4)

## Critical (P0) Missing — 보완 1순위
| ID | Requirement | Why P0 | Verbatim grep result |
|---|---|---|---|
| FR-3 | export button disabled while running | AC 본문 항목 | - |

## Detail

### Implemented
| ID | Priority | Requirement | Quote | Evidence (파일:라인) | Verbatim? |
|---|---|---|---|---|---|
| FR-4 | P1 | export menu in overflow | "toolbar overflow" | src/export/Menu.tsx:18 | N |

### Missing
| ID | Priority | Requirement | Why P{0/1/2} | Notes | Verbatim grep result |
|---|---|---|---|---|---|
| FR-1 | P1 | download filename | 보조 기능 | naming not wired | 0 |
| FR-2 | P1 | dialog title | 보조 UI 문구 | dialog uses old copy | 0 |
| FR-3 | P0 | export button disabled | AC 본문 항목 | no busy-state guard | - |
```

# Workspace state (raw command output — no interpretation supplied)

```
$ git ls-files src/export
src/export/Menu.tsx
src/export/Dialog.tsx
```

```
$ wc -l src/export/Menu.tsx src/export/Dialog.tsx
      44 src/export/Menu.tsx
      61 src/export/Dialog.tsx
     105 total
```

```
$ git grep -Fn "report-{date}.csv" .
```

```
$ git grep -Fn "Export selection" .
```

```
$ git grep -Fn "toolbar overflow" src/export/Menu.tsx
src/export/Menu.tsx:18:  // rendered inside the toolbar overflow group
```

The requirements excerpt above is the whole requirements file. It has no
`## AC` section and no Given-When-Then block.

No `docs/implementation-notes.md` in this workspace.
