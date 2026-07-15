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
4. [references/body-guide.md](references/body-guide.md)를 Read하고 그 규칙대로 본문 생성 (Korean).
5. naranizer post-pass로 어투 변환 — 프로필 없음·미설치면 스킵 (규칙: body-guide.md).
6. `gh pr create --title "..." --body "..."` 제안, 유저 확인 후 실행.

## Base Branch Detection

Auto-detect: upstream tracking > parent feature branch > origin/master > origin/main. Script: [references/base-branch-detection.md](references/base-branch-detection.md)

## Title Format
`<TICKET-ID> <primary-type>: <Subject>`
- Ticket ID: most frequent in commits, else `NO-ISSUE`
- Type priority: feat > fix > refactor > perf > chore > docs > test
- Subject: 60-72 chars, capitalized present verb

## Body Sections

섹션 5개 고정: 요약 / 주요 변경 / 확인 방법 (QA 가이드) / 배포 시 주의사항 / Linked Issues. **확인 방법 필수** — 기존 ↔ 변경 후 동작 대비 표가 본체. 재현 도구·명령은 "참고:" 힌트로만. 상세: body-guide.md

## Examples

```
# Title
PROJ-111 feat: Add order cancellation API
```

본문 예시: body-guide.md 하단 Example.

## Error Handling

- 커밋 없음 → base branch 감지 실패 가능성 안내, 수동 지정 요청.
- `gh` CLI 미설치·미인증 → 가이드 안내 후 중단.
- remote 미push → `git push -u origin <branch>` 먼저 안내.
