# nara-pr-activity-reminder — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Record PR activity — replies to your review comments, commits pushed, comments left on your own PR — onto the Multica card that already owns that PR. Creates no cards.

PR 하나 = 카드 한 장. 내가 연 PR이면 그 작업 카드에, 남이 연 PR이면 `리뷰 필요:` 판정 카드에 활동을 코멘트로 적는다. 대상 카드가 없으면 만들지 않고 건너뛴다.

## 호출

- Claude Code: `/nara-pr-activity-reminder --host <GH_HOST> --repo <OWNER/REPO> --reviewer <USER> [--mention <ID>]`
- Codex: `$nara-pr-activity-reminder ...`
- 실제로는 out-of-band 크론 스크립트가 돈다. 로직이 100% 결정론이라 LLM이 필요 없다. **오토파일럿과 동시에 돌리지 말 것** — 그 상태에서 카드가 두 배로 생겼다.

## 언제 쓰나

- **USE FOR:** "내 리뷰에 대댓글", "리뷰 중인 PR에 새 커밋", "내 PR에 누가 코멘트 달았나", "PR 활동 알림", "review activity reminder".
- **DO NOT USE FOR:** 미리뷰 PR 탐지 (→ nara-review-reminder), 실제 리뷰 작성 (→ nara-code-review / nara-pr-review), 리뷰 큐 드레인 (→ nara-review-queue).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
