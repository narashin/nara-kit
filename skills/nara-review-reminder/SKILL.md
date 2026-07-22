---
name: nara-review-reminder
description: >-
  Find open PRs where you are a requested reviewer but have not yet reviewed, and create Multica reminder issues.
  USE FOR: "리뷰 안 한 PR", "review reminder", "PR 리뷰 미완료", "review-requested but not reviewed".
  DO NOT USE FOR: actually reviewing PRs (→ nara-code-review), creating PRs (→ nara-pr).
---

# review-reminder — 미리뷰 PR 리마인더

지정된 레포에서 리뷰 요청은 받았으나 아직 리뷰를 남기지 않은 PR을 찾아 Multica 이슈로 생성한다.

## 인자 (`$ARGUMENTS`)

```
nara-review-reminder --host <GH_HOST> --repo <OWNER/REPO> --reviewer <USERNAME> [--mention <MEMBER_ID>] [--reviewer-agent <AGENT>]
```

| 인자 | 예시 | 설명 |
|------|------|------|
| `--host` | `github.com` | GitHub 호스트 (기본: `github.com`) |
| `--repo` | `org/repo` | 대상 레포 (`OWNER/REPO`) |
| `--reviewer` | `alice` | 리뷰어 username |
| `--mention` | `<MEMBER_ID>` | (선택) Multica member UUID. 지정 시 **신규 이슈**에 멘션 코멘트를 달아 알림 발송 |
| `--reviewer-agent` | `PR-Reviewer` | (선택, 기본 `PR-Reviewer`) 신규 이슈를 이 에이전트에 assign → assign 즉시 자동 리뷰 트리거. 빈 값이면 미assign(쌓이기만) |

인자 없으면 agent instructions에서 주입된 기본값 사용.

## 실행

```bash
GH_HOST=<host> gh pr list \
  --repo <OWNER/REPO> \
  --state open \
  --json number,title,url,reviewRequests,reviews \
  --limit 100
```

## 필터 조건

다음 조건을 **모두** 만족하는 PR만 대상:

1. `reviewRequests[].login` 에 `<reviewer>` 포함
2. `reviews[].author.login` 에 `<reviewer>` **없음**

## 출력 — 미리뷰 PR 없음

```
✅ 미리뷰 PR 없음 — 모든 리뷰 완료
```

## 출력 — 미리뷰 PR 있음

각 PR에 대해 Multica 이슈 생성:

```bash
# description의 개행은 셸에서 실제 개행으로 만들어 전달 (인라인 리터럴 "\n"은 백슬래시-n으로 렌더됨)
DESC=$(printf 'PR: %s\n\n리뷰 요청을 받았으나 아직 리뷰를 남기지 않은 PR입니다.' "<PR URL>")
multica issue create \
  --title "리뷰 필요: <PR 제목>" \
  --description "$DESC" \
  --priority medium \
  --assignee "<reviewer-agent>" \   # 기본 PR-Reviewer. assign 순간 자동 리뷰(nara-review-queue) 실행. 빈 값이면 생략
  --output json
# → issue ID 추출 후 metadata 저장
multica issue metadata set <issue_id> --key pr_url --value "<PR URL>"
```

이슈가 `--reviewer-agent` 에 assign되면 Multica가 해당 에이전트의 task를 enqueue → 에이전트가 nara-review-queue 스킬로 PR을 리뷰하고 결과를 이슈 코멘트(KO/EN)로 남긴 뒤 done 처리한다. 이것이 "리뷰 필요 생성 → 자동 리뷰" 트리거.

## 멘션 알림 (`--mention` 지정 시)

`--mention <MEMBER_ID>` 가 주어지면, **신규로 생성한 이슈에 한해** 멘션 코멘트를 추가하여 알림을 발송한다:

```bash
multica issue comment add <issue_id> \
  --content "[@<reviewer>](mention://member/<MEMBER_ID>) 리뷰 대기 중인 PR입니다." \
  --output json
```

- 멘션 토큰 형식: `[@<표시명>](mention://member/<MEMBER_ID>)` — 사람에게 알림 발송
- 표시명은 `--reviewer` username 사용
- **dedup으로 스킵된(이미 존재하는) 이슈에는 코멘트를 달지 않는다** → 매 실행마다 반복 알림 방지

## Dedup 규칙

이슈 생성 전 `multica issue list` 로 기존 이슈 조회:
- title에 `리뷰 필요:` + PR URL 동일한 이슈 이미 존재 → 생성 스킵 (멘션 코멘트도 스킵)
- 존재하지 않으면 생성 (+ `--mention` 지정 시 멘션 코멘트 추가)

## 규칙

- **fire-and-forget 자동화** — 헤드리스(Multica autopilot)로 도므로 인터랙티브 confirm 게이트 없음. 안전은 **dedup(중복 이슈/알림 방지) + 가역성(이슈는 삭제 가능, 코드 변경 없음)**으로 확보. 인간 확인이 필요한 실행이면 이 스킬 대신 수동 리뷰.
- `GH_HOST` 환경변수로 gh CLI 라우팅 제어
- 인자 누락 시 agent instructions 기본값 사용. 그것도 없으면 오류 안내 후 중단
- `gh` CLI PATH에 존재해야 함
- `--mention` 미지정 시 멘션 코멘트 단계는 전체 스킵 (기존 동작 그대로)
