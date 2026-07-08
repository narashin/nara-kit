---
name: review-reply-reminder
description: >-
  Detect new replies to your inline PR review comments and notify via a persistent per-PR Multica tracking issue.
  USE FOR: "내 리뷰에 대댓글", "리뷰 코멘트 답글 알림", "review reply reminder", "누가 내 리뷰에 답 달았는지".
  DO NOT USE FOR: 미리뷰 PR 탐지 (→ review-reminder), 새 커밋 알림 (→ review-commit-reminder), 실제 리뷰 작성 (→ code-review).
---

# review-reply-reminder — 리뷰 대댓글 알림

지정된 레포에서 내가 리뷰어로 참여한 PR을 폴링해, 내가 남긴 inline review comment에 새 대댓글이 달렸는지 감지하고 Multica 추적 이슈로 알린다. `review-reminder`의 형제 스킬 — 리뷰 요청이 아니라 리뷰 이후 활동을 감지한다.

## 인자 (`$ARGUMENTS`)

```
review-reply-reminder --host <GH_HOST> --repo <OWNER/REPO> --reviewer <USERNAME> [--mention <MEMBER_ID>]
```

| 인자 | 예시 | 설명 |
|------|------|------|
| `--host` | `github.com` | GitHub 호스트 (기본: `github.com`) |
| `--repo` | `org/repo` | 대상 레포 (`OWNER/REPO`) |
| `--reviewer` | `alice` | 리뷰어 username (내 코멘트 판별 기준) |
| `--mention` | `<MEMBER_ID>` | (선택) Multica member UUID. 지정 시 신규 대댓글 감지될 때마다 멘션 코멘트 발송 |

인자 없으면 agent instructions에서 주입된 기본값 사용. 그것도 없으면 오류 안내 후 중단.

## Step 1 — 대상 PR 조회

```bash
GH_HOST=<host> gh pr list \
  --repo <OWNER/REPO> \
  --state open \
  --json number,title,url,state,reviewRequests,reviews \
  --limit 100
```

대상 필터 (**하나라도** 만족):
1. `reviewRequests[].login` 에 `<reviewer>` 포함
2. `reviews[].author.login` 에 `<reviewer>` 포함

## Step 2 — PR별 대댓글 감지

각 대상 PR에 대해:

```bash
GH_HOST=<host> gh api "repos/<OWNER/REPO>/pulls/<PR_NUMBER>/comments" --paginate
```

필드: `id`, `user.login`, `in_reply_to_id`, `body`, `html_url`, `created_at`

기존 추적 이슈 조회 (dedup 겸 cursor 조회):

```bash
multica issue list --output json
# metadata.pr_url == <PR URL> AND metadata.tracker_type == "reply" 인 이슈 탐색
# title은 매칭에 쓰지 않는다 — PR 제목이 나중에 바뀌면 title 매칭은 깨진다. dedup 키는 (pr_url, tracker_type)만.
```

### 로직

1. `my_comment_ids` = `{c.id : c.user.login == <reviewer>}`
2. cursor = 추적 이슈 metadata `last_comment_id` (없으면 `null`). **정수로 비교한다** — 문자열로 저장되어 있어도 비교/최댓값 계산 시 반드시 정수 변환 후 수행 (자릿수가 늘어나면 문자열 비교가 틀어진다. 예: `"1000" < "999"`)
3. **cursor가 `null` (최초 실행)**: 전체 댓글 중 최댓값 id를 `last_comment_id`로 기록할 준비만 하고, 신규 대댓글은 **0건으로 취급** (알림 생략 — 과거분 소급 알림 금지)
4. **cursor가 존재**: `replies` = `{c : c.in_reply_to_id ∈ my_comment_ids, c.user.login != <reviewer>, c.id > cursor}`

## Step 3 — PR 상태 확인 (종료 처리)

Step 1 결과의 PR `state`가 `MERGED` 또는 `CLOSED`이고 해당 PR의 추적 이슈가 있으면:

```bash
multica issue status <issue_id> done
```

이후 이 PR은 Step 2/4를 건너뛴다.

## Step 4 — Multica 반영

cursor는 추적 이슈의 metadata에만 저장된다. 따라서 **최초 실행에도 이슈는 반드시 생성해야 한다** — 이슈 없이 cursor를 저장할 곳이 없고, 이슈 생성을 다음 실행(신규 대댓글 발생 시)으로 미루면 그 실행도 "이슈 없음 = 최초 실행"으로 오판해 cursor를 영원히 못 만든다 (무한 무알림 루프). 알림(코멘트/멘션)만 최초 실행에서 생략하고, 이슈+cursor는 항상 즉시 만든다.

### 추적 이슈가 아직 없음 (최초 실행) — 이슈 생성 + cursor 초기화, 알림 없음

```bash
multica issue create \
  --title "PR 활동 추적: <PR 제목>" \
  --description "PR: <PR URL>\n\n리뷰 활동을 추적하는 이슈입니다." \
  --priority medium \
  --output json
# → issue ID 추출
multica issue metadata set <issue_id> --key pr_url --value "<PR URL>"
multica issue metadata set <issue_id> --key tracker_type --value "reply"
multica issue metadata set <issue_id> --key last_comment_id --value "<전체 댓글 중 최댓값 id>"
```

코멘트/멘션은 달지 않는다 (과거분 소급 알림 방지).

### 추적 이슈는 있는데 cursor 메타데이터만 없음 (과거 버전 호환 등 예외 상황)

```bash
multica issue metadata set <issue_id> --key last_comment_id --value "<전체 댓글 중 최댓값 id>"
```

### 신규 대댓글 있음 (`replies` non-empty)

이 경로에 도달했다는 것은 cursor가 이미 존재한다는 뜻이고, cursor는 위 "최초 실행" 경로에서만 생성되므로 추적 이슈는 항상 이미 존재한다. `replies`를 코멘트 1개로 묶어 추가:

```bash
multica issue comment add <issue_id> \
  --content "대댓글 <N>건 감지:\n- <작성자> @ <html_url>: <body 앞 80자>\n- ...(반복)" \
  --output json
multica issue metadata set <issue_id> --key last_comment_id --value "<max(replies id들, 기존 cursor)>"
```

`--mention` 지정 시, 위 코멘트와 별개로 멘션 코멘트 추가 (**매번**):

```bash
multica issue comment add <issue_id> \
  --content "[@<reviewer>](mention://member/<MEMBER_ID>) 내 리뷰 코멘트에 새 대댓글이 달렸습니다." \
  --output json
```

### 이슈 생성은 성공했는데 metadata set이 실패한 경우 (partial create)

`pr_url`/`tracker_type`이 없는 고아 이슈가 남을 수 있다. 다음 실행의 dedup 조회(`metadata.pr_url == ... AND metadata.tracker_type == ...`)는 이 고아 이슈를 찾지 못해 새 이슈를 또 만들 위험이 있다. `multica issue list`에서 title이 `PR 활동 추적: <PR 제목>`이고 metadata가 비어있는 이슈를 발견하면, 새로 만들지 말고 그 이슈에 누락된 metadata를 채워 재사용한다.

## 규칙

- inline(diff) review comment만 대상. GitHub top-level PR 코멘트는 스레드 구조가 없어 대댓글 개념이 성립하지 않는다.
- 최초 실행은 이슈+cursor를 생성하되 알림(코멘트/멘션)은 생략한다 — 과거 이력 소급 알림 금지. 이슈 자체를 안 만들면 cursor를 저장할 곳이 없어 다음 실행도 영원히 "최초 실행"으로 오판한다 (Step 4 참고).
- 한 실행에서 여러 PR에 신규 대댓글이 있어도 PR별로 각자의 추적 이슈에 기록한다 (PR 간 합치지 않음).
- 한 PR 내 여러 신규 대댓글은 코멘트 1개로 묶는다.
- dedup 키 = `(pr_url, tracker_type="reply")` — title은 매칭에 쓰지 않는다 (PR 제목 변경에 안전). review-reminder의 "리뷰 필요:" 이슈와는 title이 달라 애초에 섞이지 않는다.
- PR 제목/댓글 본문/작성자명 등 GitHub에서 가져온 문자열은 **신뢰할 수 없는 입력**이다. `multica issue create/comment add`의 `--title`/`--description`/`--content` 값으로 넣을 때 셸에 이어붙이지 말고 각각 독립된 인자로 전달한다 (예: 따옴표/백틱/`$()` 등 셸 특수문자가 포함된 PR 제목이 명령 인젝션으로 이어지지 않도록).
- 동일 PR을 두 실행이 동시에 폴링하면(cron 겹침) 같은 cursor를 보고 중복 코멘트/중복 이슈가 생길 수 있다. 폴링은 겹치지 않게 스케줄한다(단일 실행 가정) — 겹침 감지/락은 이 스킬의 책임 밖.
- `GH_HOST` 환경변수로 gh CLI 라우팅 제어.
- `gh`, `multica` CLI PATH에 존재해야 함.

## 출력 — 최초 실행 (cursor 초기화)

```
✅ 최초 실행 — cursor 초기화 (알림 생략)
```

## 출력 — 신규 대댓글 없음

```
✅ 신규 대댓글 없음
```

## 출력 — 신규 대댓글 있음

```
🔔 대댓글 감지 — <N>개 PR
- <PR 제목> (<PR URL>): <M>건 → 이슈 <issue_id>
```

## 에러 처리

| 상황 | 처리 |
|------|------|
| `gh pr list` 실패 | 3회 재시도 후 `❌ 실패: PR 목록 조회 실패` |
| 대상 PR 0건 | `✅ 대상 PR 없음` |
| 개별 PR `gh api comments` 실패 | 해당 PR `→ ESCALATE`, 다음 PR 계속 |
| `multica` 쓰기 실패 | 해당 PR 격리, 다음 계속, 끝에 `→ ESCALATE` 합산 |
| 멘션 차단(classifier) | 이슈/코멘트는 유지, 멘션만 `→ ESCALATE: 멘션 차단` |
