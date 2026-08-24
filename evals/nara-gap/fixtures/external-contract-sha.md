# docs/requirements.md (excerpt)

- [ ] FR-1: The account detail header should show the account display name.
- [ ] FR-2: The account detail header should show the member count.
- [ ] FR-3: The record list should show the owning group per row.
- [ ] FR-4: The account payload must carry `serviceRoleArn` for the role panel.
- [ ] FR-5: The account payload must carry `policyDomain` for the role panel.

# docs/gap.md (existing — produced by a previous run)

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: 2026-07-01
- External contracts: billing-api@a1b2c3d (resolved 2026-07-01)
- Score: 100/100
- **Gate: ✅ review-ready**

## Summary
- Total: 5 | Implemented: 5 | Partial: 0 | Missing: 0 | Agreed Exception: 0
- **P0 Missing (Critical): 0**
- Needs Confirm: 0 (정족수 0 — §4)

## Detail

### Implemented
| ID | Priority | Requirement | Quote | Evidence (파일:라인) | Verbatim? | Why sampled |
|---|---|---|---|---|---|---|
| FR-1 | P1 | account display name | "display name" | src/account/Header.tsx:31 | N | - |
| FR-2 | P1 | member count | "member count" | src/account/Header.tsx:44 | N | - |
| FR-3 | P1 | owning group per row | "owning group" | src/record/Row.tsx:57 | N | - |
| FR-4 | P0 | role arn in payload | `serviceRoleArn` | billing-api@a1b2c3d:src/dto/AccountDto.java:44 | Y | - |
| FR-5 | P0 | policy domain in payload | `policyDomain` | billing-api@a1b2c3d:src/dto/AccountDto.java:51 | Y | - |
```

# Workspace state (raw command output — no interpretation supplied)

```
$ git ls-files | grep -c billing-api
0
```

```
$ git cat-file -e a1b2c3d
fatal: Not a valid object name a1b2c3d
```

```
$ git remote -v
origin	git@example.com:web/console-ui.git (fetch)
origin	git@example.com:web/console-ui.git (push)
```

```
$ wc -l src/account/Header.tsx src/record/Row.tsx
      92 src/account/Header.tsx
      70 src/record/Row.tsx
     162 total
```

```
$ git grep -Fn "serviceRoleArn" .
src/account/RolePanel.tsx:22:  const arn = account.serviceRoleArn
```

```
$ git grep -Fn "policyDomain" .
src/account/RolePanel.tsx:23:  const domain = account.policyDomain
```

No `docs/implementation-notes.md` in this workspace.
