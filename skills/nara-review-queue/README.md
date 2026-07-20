# nara-review-queue — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Drain Multica "리뷰 필요" reminder issues: trigger /review per linked PR, write each verdict back as an issue comment.

## 호출

- Claude Code: `/nara-review-queue`
- Codex: `$nara-review-queue`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "쌓인 리뷰 처리", "멀티카 리뷰 큐", "review-queue", a nara-review-reminder issue URL/ID.
- **DO NOT USE FOR:** creating reminders (→ nara-review-reminder), local commit review (→ nara-code-review), comments on my own PR (→ nara-pr-respond).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
