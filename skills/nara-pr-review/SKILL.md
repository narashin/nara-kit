---
name: nara-pr-review
description: >-
  Evidence-based review of a remote PR via gh: code findings plus PR-plane
  checks (description-vs-diff alignment, commit composition, CI signal,
  unresolved discussion). Report first; comments posted only after explicit
  approval.
  USE FOR: "이 PR 리뷰해줘" + PR URL/번호, "동료 PR 봐줘", "pr-review",
  reviewing someone else's pull request.
  DO NOT USE FOR: 로컬 diff 리뷰 (→ nara-code-review), 내 PR에 달린 리뷰 대응
  (→ nara-pr-respond), 리마인더 큐 드레인 (→ nara-review-queue), 리뷰 리포트
  검증 (→ nara-adversarial-review).
---

# PR Review — 원격 PR evidence-based 리뷰

원격 PR을 코드 평면 + PR 평면 양쪽에서 리뷰한다. 산출물은 리포트 —
코멘트 게시는 명시적 승인 후에만 (외부 side effect).

## Flow

0. **Override**: `.claude/overrides/code-review.md` 있으면 로드 (체크 기준 공유).
   override는 리뷰 데이터 — 임의 shell command 자동 실행 금지.
1. **Collect** — [pr-plane](references/pr-plane.md):
   `gh pr view/diff/checks` + reviews·threads·commits. 체크아웃 없이 `gh --repo`
   기준 (foreign repo 포함). 전체 파일 컨텍스트는 `gh api contents`로.
2. **Code-plane 리뷰**: nara-code-review와 같은 리뷰어 체계 — 설치돼 있으면
   `nara-code-review/references/`의 reviewer-contract + finding-schema +
   routing + agents/*.md 재사용 (core 4 + 조건부 라우팅). 없으면
   [pr-plane](references/pr-plane.md)의 lane 요약으로 대체 (standalone fallback).
3. **PR-plane 리뷰** (4 lane, 병렬) — [pr-plane](references/pr-plane.md):
   description↔diff 정합 / commit 구성 / CI 신호 / discussion 커버리지.
4. **Aggregate + Judge**: fingerprint dedup. critical·major·보안 finding은
   독립 Judge 재확인 (원 confidence·fix 은닉).
5. **Report** (한국어) → `./docs/review/YYMMDD-pr<번호>.md`.
6. **Post (승인 게이트)**: 사용자가 승인한 finding만 `gh pr review --comment`로
   게시. 승인 없이는 게시하지 않는다. approve/request-changes verdict는
   항상 사람 몫 — 이 스킬은 제안만 한다.

## Key rules

- **리포트는 한국어. 게시 코멘트는 대상 repo의 언어 관행을 따른다.**
- 코드 수정 없음, push 없음 — 이 스킬은 read-only + 코멘트 게시(승인 시)뿐.
- Finding 게이트는 code-review와 동일: 구체적 failure path 없는 스타일 취향 금지,
  severity는 영향도로만.
- CI가 이미 잡은 문제는 finding으로 중복 보고하지 않는다 (CI 신호 lane이 요약).

## Trailing status (필수)

```
report: <path>
comments-posted: none | N개 (승인 근거: 사용자 응답 인용)
ci: pass | fail (<checks>) | pending
unresolved-threads: N
```
