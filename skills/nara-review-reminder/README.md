# nara-review-reminder — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Find open PRs where you are a requested reviewer but have not yet reviewed, and create Multica reminder issues.

## 호출

- Claude Code: `/nara-review-reminder`
- Codex: `$nara-review-reminder`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "리뷰 안 한 PR", "review reminder", "PR 리뷰 미완료", "review-requested but not reviewed".
- **DO NOT USE FOR:** actually reviewing PRs (→ nara-code-review), creating PRs (→ nara-pr).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
