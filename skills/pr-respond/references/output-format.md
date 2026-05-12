# PR Respond Output Format

## Standard Output

```
## PR Review Response -- PR #{number}

### Summary
- Total comments: N
- Accepted (implemented): N
- Rebutted (replied): N
- Questions answered: N
- Skipped (praise): N
- On hold: N (user confirmation needed)

### Accepted (implemented)
| # | File:Line | Reviewer | Summary | Action |
|---|-----------|----------|---------|--------|
| 1 | src/auth.ts:42 | @reviewer | null check missing | Fixed. early return added |

### Rebutted
| # | File:Line | Reviewer | Summary | Rebuttal Reason |
|---|-----------|----------|---------|-----------------|
| 1 | src/api.ts:15 | @reviewer | remove legacy code | backward compat needed (target: iOS 13+) |

### On Hold (user confirmation needed)
| # | File:Line | Reviewer | Summary | Issue |
|---|-----------|----------|---------|-------|
| 1 | src/utils.ts:88 | @reviewer | refactoring proposal | architecture direction decision needed |

### Questions Answered
| # | File:Line | Reviewer | Question | Answer |
|---|-----------|----------|----------|--------|
| 1 | src/hooks.ts:20 | @reviewer | why useMemo? | render optimization -- parent re-renders frequently |
```

## --status Mode Output

```
## PR #{number} -- Unreplied Review Comments

| # | Category | File:Line | Reviewer | Summary |
|---|----------|-----------|----------|---------|
| 1 | blocking | src/auth.ts:42 | @reviewer | null check missing |
| 2 | suggestion | src/api.ts:15 | @reviewer | error handling improvement |

Total N unreplied
```

## --dry-run Mode Output

Same structure as standard but with "(dry-run)" in title, "planned" instead of "implemented", and no code changes or replies posted.
