# nara-pr-activity-reminder — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Detect new replies to your PR review comments AND new commits pushed to PRs you review, notifying via ONE persistent per-PR Multica tracking issue. 예전 `review-reply-reminder` + `review-commit-reminder`를 하나로 합친 것 — PR 하나 = 추적 이슈 하나.

## 호출

- Claude Code: `/nara-pr-activity-reminder --host <GH_HOST> --repo <OWNER/REPO> --reviewer <USER> [--mention <ID>]`
- Codex: `$nara-pr-activity-reminder ...`
- 보통 Multica autopilot(PR-Activity-Reminder agent)이 repo별로 자동 실행

## 언제 쓰나

- **USE FOR:** "내 리뷰에 대댓글", "리뷰 중인 PR에 새 커밋", "PR 활동 알림", "review activity reminder".
- **DO NOT USE FOR:** 미리뷰 PR 탐지 (→ nara-review-reminder), 실제 리뷰 작성 (→ nara-code-review / nara-pr-review), 리뷰 큐 드레인 (→ nara-review-queue).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
