---
name: nara-pr
description: >-
  Analyze commits against the auto-detected base branch and generate a Pull Request title and body in Korean.
  USE FOR: "pr", "PR 만들어", "pull request", "PR 제목", "/nara-pr".
  DO NOT USE FOR: git commit, branch management, code review.
---

# pr — Smart PR Generator

## Steps

1. 아래 스크립트로 base branch 자동 감지.
2. `git log $BASE..HEAD --oneline`으로 커밋 목록 수집.
3. 커밋 분석 → Title Format 규칙에 따라 제목 생성.
4. Body Sections 규칙에 따라 본문 생성 (Korean).
5. `gh pr create --title "..." --body "..."` 명령 제안. 유저 확인 후 실행.

## Base Branch Detection

Auto-detect base: upstream tracking > parent feature branch > origin/master > origin/main. See [references/base-branch-detection.md](references/base-branch-detection.md) for script.

## Title Format
`<TICKET-ID> <primary-type>: <Subject>`
- Ticket ID: most frequent from commits (PROJ-###, etc.). None → `NO-ISSUE`
- Primary type priority: feat > fix > refactor > perf > chore > docs > test
- Subject: 60-72 chars, capitalized present verb

## Body Sections
- Overview (2-4 bullets, why + user impact)
- Changes (grouped by type)
- Breaking Changes
- Affected Areas / Risk
- Validation
- Rollout / Backout
- Linked Issues (`Closes TICKET-ID`)

## Examples

```
# Title
PROJ-111 feat: Add order cancellation API

# Body (Korean)
## 개요
- 주문 취소 API 신규 추가 (사용자 요청 기반)
- 취소 사유 기록 및 환불 트리거 포함
```

## Error Handling

- 커밋 없음 (`git log` 결과 비어있음) → base branch 감지 실패 가능성 안내, 수동 지정 요청.
- `gh` CLI 미설치 또는 미인증 → 설치/인증 가이드 안내 후 중단.
- remote에 push 안 됨 → `git push -u origin <branch>` 먼저 실행 안내.
