# PR Respond Output Format

> output-contract receipt + verification preview 두 단을 합친 형식.
> Receipt = 영수증 (자동화/스캔용), Tables = 사용자 검수용 preview.
> 항상 둘 다 출력. 플래그 없음 (human usability first).

## Receipt Header (필수, 먼저 출력)

```
PR #<N> 리뷰 대응 완료.
- comments processed: <N>
- accepted: <n> (implemented) · rebutted: <n> · follow-up: <n> · on hold: <n>
- side effects:
  - github: <n> replies posted, <n> code changes pushed, <n> threads resolved, re-review requested: <logins | none>
- artifact: PR thread (#<N>)
- next: hold 항목 사용자 결정 또는 reviewer 응답 대기
```

Receipt는 [nara-kit 출력 계약](../../nara-now/references/output-contract.md)의 `/nara-pr-respond` 템플릿 그대로 (파일이 없으면 이 문서의 Receipt Header가 기준).

## Standard Output (Receipt + Verification Preview)

Receipt header 출력 후 아래 표 이어서:

```
## PR Review Response -- PR #{number}

### Summary
- Total comments: N
- Accepted (implemented): N
- Rebutted (replied): N
- Questions answered: N
- Asked (posed to reviewer): N
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

### Asked (posed to reviewer)
| # | File:Line | Reviewer | Category | Our Recommendation | Evidence |
|---|-----------|----------|----------|--------------------|----------|
| 1 | src/x.ts:10 | @reviewer | source-conflict | keep current -- matches spec §3 | requirements.md:42, src/x.ts:10 |

### Follow-up (out of scope for this PR)
| # | File:Line | Reviewer | Summary | Why out of scope | Issue |
|---|-----------|----------|---------|------------------|-------|
| 1 | src/api.ts:34 | @reviewer | env var unvalidated | unchanged line, blame 1a2b3c4 (3 months before PR) | not created |

### Publication plan (CHECKPOINT: nothing runs until approved)
| # | Step | Target | Command |
|---|------|--------|---------|
| a | push | feature/x | `git push origin feature/x` |
| b | reply | 9001 | `gh api .../comments/9001/replies -f body=...` |
| c | resolve | PRRT_kwA1 | `gh api graphql ... resolveReviewThread ...` |
| d | re-review | @reviewer | `gh pr edit 57 --add-reviewer reviewer` |
```

Before approval the receipt header reads `PR #<N> 리뷰 대응: 승인 대기`, `implemented` reads `planned`, and every github count is 0.

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
