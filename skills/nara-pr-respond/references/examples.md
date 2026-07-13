# PR Respond Examples

## Example 1: Standard Execution

Situation: PR #142 with 3 review comments

Comment 1: @senior-dev on src/auth.ts:42 -- "validateToken에서 null check 빠져있음. token이 undefined일 때 crash 발생"
Comment 2: @senior-dev on src/api.ts:15 -- "이 레거시 헬퍼 제거하고 새 유틸로 교체하는 게 낫지 않나?"
Comment 3: @senior-dev on src/hooks.ts:20 -- "👍 깔끔하네요"

Result:

```
## PR Review Response -- PR #142

### Summary
- Total comments: 3
- Accepted (implemented): 1
- Rebutted (replied): 1
- Skipped (praise): 1

### Accepted (implemented)
| # | File:Line | Reviewer | Summary | Action |
|---|-----------|----------|---------|--------|
| 1 | src/auth.ts:42 | @senior-dev | null check missing | Fixed. early return added + unit test reinforced |

Side-effect analysis: validateToken caller 3 sites confirmed (LoginForm, AuthGuard, TokenRefresh). All callers use optional chaining for null return -> no regression.

### Rebutted
| # | File:Line | Reviewer | Summary | Rebuttal Reason |
|---|-----------|----------|---------|-----------------|
| 1 | src/api.ts:15 | @senior-dev | remove legacy helper | legacyHelper is actively used by MobileClientAdapter for v2 API fallback. Removal breaks backward compat. |

Reply: "legacyHelper is actively used by MobileClientAdapter for v2 API fallback (src/adapters/MobileClientAdapter.ts:34). Removing it breaks backward compat for clients not yet migrated to v3."
```

## Example 2: --dry-run Mode

```
## PR Review Response -- PR #89 (dry-run)

### Summary
- Total comments: 2
- Planned accepts: 1
- On hold: 1

### Planned Accepts (not implemented -- dry-run)
| # | File:Line | Reviewer | Summary | Plan |
|---|-----------|----------|---------|------|
| 1 | src/utils.ts:55 | @reviewer | hardcoded error message | Extract to constant. Scope: this file only. No side effects |

### On Hold
| # | File:Line | Reviewer | Summary | Issue |
|---|-----------|----------|---------|-------|
| 1 | src/store.ts:12 | @reviewer | Redux -> Zustand migration | Architecture direction decision needed. Redux pattern used project-wide |
```

## Example 3: --status Mode

```
## PR #142 -- Unreplied Review Comments

| # | Category | File:Line | Reviewer | Summary |
|---|----------|-----------|----------|---------|
| 1 | blocking | src/auth.ts:42 | @senior-dev | null check missing |
| 2 | suggestion | src/api.ts:15 | @senior-dev | replace legacy helper |

Total 2 unreplied
```
