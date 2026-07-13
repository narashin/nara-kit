---
name: nara-review-queue
description: >-
  Drain Multica "리뷰 필요" reminder issues: trigger /review per linked PR, write each verdict back as an issue comment.
  USE FOR: "쌓인 리뷰 처리", "멀티카 리뷰 큐", "review-queue", a nara-review-reminder issue URL/ID.
  DO NOT USE FOR: creating reminders (→ nara-review-reminder), local commit review (→ nara-code-review), comments on my own PR (→ nara-pr-respond).
---

# review-queue — 멀티카 리뷰 큐 드레인

`nara-review-reminder` 가 멀티카에 쌓아둔 "리뷰 필요" 이슈를 읽어, 각 PR에 대해 내장 `review` 스킬을 트리거하고 결과를 이슈 코멘트로 되돌려쓴다. nara-review-reminder(생산자)의 소비자 짝.

## 인자 (`$ARGUMENTS`)

```
nara-review-queue [<issue-id | url>] [--limit N] [--done-status S]
```

| 인자 | 기본 | 설명 |
|------|------|------|
| `<issue-id \| url>` | — | 단일 이슈만 처리. `.../issues/<uuid>` URL이면 UUID 추출. 생략 시 큐 전체 |
| `--limit` | `50` | 큐 모드 최대 처리 건수 |
| `--done-status` | `done` | 완료 후 전환할 status (보드 컬럼명에 맞춰 override) |

리뷰 결과는 **멀티카 이슈 코멘트로만** 기록한다 — 원격 PR에는 절대 게시하지 않는다.

## Step 0 — Pre-flight

`multica`, `gh` PATH 확인 (없으면 `❌ 실패` 후 중단). 인자가 URL이면 `issues/` 뒤 UUID 추출.

## Step 1 — 큐 선택

큐 모드: `multica issue list --status todo --limit <N> --output json`.
단일 모드: `multica issue get <id> --output json`.

대상 조건 (모두 만족): `title` 이 `리뷰 필요:` 로 시작 · `metadata.pr_url` 존재 · `metadata.reviewed != true`.
0건 → `✅ 리뷰 대기 큐 비어있음` 후 종료.

## Step 2 — PR별 리뷰

`number` 오름차순으로 순회. 각 이슈마다:

1. `metadata.pr_url` 에서 PR URL 추출. URL hostname → `GH_HOST` (레포마다 다를 수 있음).
2. `(i/total)` 진행 보고 (출력 계약 §7).
3. `GH_HOST` export 후 내장 `review` 스킬을 Skill 도구로 호출 (인자 = PR URL).
   엔터프라이즈 호스트를 못 다루면 fallback: `GH_HOST=<host> gh pr diff <url>` 로 diff 받아 직접 리뷰.

## Step 3 — 리뷰 코멘트 처리

리뷰 산출물의 종착지는 **원본 멀티카 이슈** — 트래커 안에서 리마인더 옆에 닫힌다. 동일 리뷰를 **한국어 + 영어 2개 코멘트**로 기록(같은 내용, 언어만 다름) 후 완료 표시:

```bash
multica issue comment add <id> --content-file <ko.md>         # 한국어 본문 (다줄은 --content-file, 또는 --content)
multica issue comment add <id> --content-file <en.md>         # 영어 본문
multica issue metadata set <id> --key reviewed --value true   # dedup source of truth (KV는 항상 유효)
multica issue status <id> <done-status>                       # positional. 유효값: backlog todo in_progress in_review done blocked cancelled
```

## 규칙

- 원격 PR에는 리뷰를 게시하지 않는다 (read-only). 결과는 멀티카 이슈에만.
- `GH_HOST` 는 PR URL에서 매번 도출. 호스트 하드코딩 금지.
- 한 건 실패해도 큐를 멈추지 말고 `❌` 표시 후 다음 건 진행. 끝에 실패 합산.

## Receipt

```
리뷰 큐 드레인 완료 (read-only).
- processed: <N>건 (reviewed <n> · skipped <n> · failed <n>)
- side effects:
  - multica: <n> comments added, <n> issues → <done-status>
- next: <멀티카 이슈 코멘트에서 리뷰 결과 확인 | 실패 건 수동 확인>
```
