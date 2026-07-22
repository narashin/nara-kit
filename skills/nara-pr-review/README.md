# nara-pr-review — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

원격 PR evidence-based 리뷰 (gh 기반, 체크아웃 없음): 코드 평면(nara-code-review
리뷰어 체계 재사용) + PR 평면(description↔diff 정합 / commit 구성 / CI 신호 /
discussion 커버리지). 리포트 우선 — 코멘트 게시는 finding 단위 승인 후에만,
approve/request-changes는 항상 사람이.

## 호출

- Claude Code: `/nara-pr-review <PR URL|번호>`
- Codex: `$nara-pr-review`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "이 PR 리뷰해줘" + PR URL/번호, "동료 PR 봐줘", "pr-review", reviewing someone else's pull request.
- **DO NOT USE FOR:** 로컬 diff 리뷰 (→ nara-code-review), 내 PR에 달린 리뷰 대응 (→ nara-pr-respond), 리마인더 큐 드레인 (→ nara-review-queue), 리뷰 리포트 검증 (→ nara-adversarial-review).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
