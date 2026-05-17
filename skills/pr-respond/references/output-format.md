# PR Respond Output Format

> output-contract receipt + verification preview 두 단을 합친 형식.
> Receipt = 영수증 (자동화/스캔용), Tables = 사용자 검수용 preview.
> 항상 둘 다 출력. 플래그 없음 (human usability first).

## Receipt Header (필수, 먼저 출력)

```
PR #<N> 리뷰 대응 완료.
- comments processed: <N>
- accepted: <n> (implemented) · rebutted: <n> · on hold: <n>
- side effects:
  - github: <n> replies posted, <n> code changes pushed
- artifact: PR thread (#<N>)
- next: hold 항목 사용자 결정 또는 reviewer 응답 대기
```

Receipt는 nara-kit output-contract `/pr-respond` 템플릿 그대로 (CLAUDE.md 자동 상속).

## Standard Output (Receipt + Verification Preview)

Receipt header 출력 후 아래 표 이어서:

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

Receipt header(`comments processed: 0`) 생략 가능. 미답 코멘트 표만 출력.

```
## PR #{number} -- Unreplied Review Comments

| # | Category | File:Line | Reviewer | Summary |
|---|----------|-----------|----------|---------|
| 1 | blocking | src/auth.ts:42 | @reviewer | null check missing |
| 2 | suggestion | src/api.ts:15 | @reviewer | error handling improvement |

Total N unreplied
```

## --dry-run Mode Output

Receipt header에 `(dry-run)` 명시, side effects는 `github: 0 (dry-run)`, "implemented"는 "planned"로 변경. 본문 표는 standard와 동일 구조.
