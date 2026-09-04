---
name: nara-pr-activity-reminder
description: >-
  Detect new replies to your PR review comments AND new commits pushed to PRs you review, notifying via ONE persistent per-PR Multica tracking issue.
  USE FOR: "내 리뷰에 대댓글", "리뷰 중인 PR에 새 커밋", "PR 활동 알림", "review activity reminder", "누가 내 리뷰에 답 달았는지", "리뷰이가 커밋 올렸는지".
  DO NOT USE FOR: 미리뷰 PR 탐지 (→ nara-review-reminder), 실제 리뷰 작성 (→ nara-code-review / nara-pr-review), 리뷰 큐 드레인 (→ nara-review-queue).
---

# nara-pr-activity-reminder — PR 리뷰 활동 알림 (대댓글 + 새 커밋, 통합)

지정된 레포에서 내가 리뷰어로 참여한 PR을 폴링해, **(1) 내 inline review comment에 새 대댓글** + **(2) 저자가 push한 새 커밋**을 감지하고 **PR당 하나의 Multica 추적 이슈**로 알린다. 예전 `review-reply-reminder` + `review-commit-reminder` 두 스킬을 하나로 합친 것 — PR 하나 = 추적 이슈 하나. `nara-review-reminder`(미리뷰 PR 탐지)의 형제 스킬.

> **이 로직은 100% 결정론 — classify/의미 판단이 전혀 없다** (gh api 조회 + cursor 비교 + multica 쓰기뿐). 따라서 **헤드리스 LLM 오토파일럿이 아니라 out-of-band 셸/스크립트 크론으로 실행**하는 것이 정석 — 빈 런 LLM 토큰 낭비도, codex inactivity 타임아웃도 없다. 이 파일은 그 스크립트의 **로직 스펙**이다 (참조 구현: `gh` + `multica` CLI + cursor).

## 인자 (`$ARGUMENTS`)

```
nara-pr-activity-reminder --host <GH_HOST> --repo <OWNER/REPO> --reviewer <USERNAME> [--mention <MEMBER_ID>]
```

| 인자 | 예시 | 설명 |
|------|------|------|
| `--host` | `github.com` | GitHub 호스트 (기본: `github.com`) |
| `--repo` | `org/repo` | 대상 레포 (`OWNER/REPO`) |
| `--reviewer` | `alice` | 리뷰어 username (내 코멘트 판별 기준) |
| `--mention` | `<MEMBER_ID>` | (선택) Multica member UUID. 지정 시 신규 활동 감지 때마다 멘션 코멘트 발송 |

인자 없으면 agent instructions에서 주입된 기본값 사용. 그것도 없으면 오류 안내 후 중단.

## Step 1 — 대상 PR 조회 (한 번)

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

## Step 2 — 추적 이슈 조회 (PR당 1개, dedup=pr_url)

```bash
multica issue list --output json
# metadata.pr_url == <PR URL> 이고 status ∈ {todo, in_progress, in_review, blocked} 인 이슈 탐색
# dedup 키는 pr_url 하나. title은 매칭에 쓰지 않는다 (PR 제목이 바뀌어도 안전).
# done/cancelled 이슈는 무시한다 — 이미 종료된 추적 (구 스킬의 reply/commit 분리 이슈 잔재 포함).
```

한 PR에 open 추적 이슈가 여럿 발견되면(구버전 잔재 등) 가장 오래된 것 하나만 쓰고 나머지는 건드리지 않는다 (병합은 이 스킬 책임 밖 — 마이그레이션은 배포 시 1회).

## Step 3 — 대댓글 감지

```bash
GH_HOST=<host> gh api "repos/<OWNER/REPO>/pulls/<PR_NUMBER>/comments" --paginate
```

필드: `id`, `user.login`, `in_reply_to_id`, `body`, `html_url`, `created_at`

### 로직

1. `my_comment_ids` = `{c.id : c.user.login == <reviewer>}`
2. cursor_reply = 추적 이슈 metadata `last_comment_id` (없으면 `null`). **정수로 비교한다** — 문자열로 저장돼 있어도 비교/최댓값 계산 시 반드시 정수 변환 후 (자릿수 늘면 문자열 비교가 틀어짐. 예: `"1000" < "999"`)
3. **cursor_reply가 `null` (이 PR 최초 추적)**: 전체 댓글 중 최댓값 id를 기록할 준비만, 신규 대댓글은 **0건** (과거분 소급 알림 금지)
4. **cursor_reply 존재**: `new_replies` = `{c : c.in_reply_to_id ∈ my_comment_ids, c.user.login != <reviewer>, c.id > cursor_reply}`

## Step 4 — 새 커밋 감지

```bash
GH_HOST=<host> gh api "repos/<OWNER/REPO>/pulls/<PR_NUMBER>/commits" --paginate
```

필드: `sha`, `commit.message`, `commit.author.date`. 배열은 오래된 순 — 마지막 원소가 최신.

### 로직

1. `latest_sha` = 배열 마지막 원소의 `sha`
2. cursor_commit = 추적 이슈 metadata `last_commit_sha` (없으면 `null`)
3. **cursor_commit `null` (최초 추적)**: 알림 생략, `latest_sha`만 기록 준비
4. **cursor_commit 존재 & `latest_sha != cursor_commit`**: `new_commits` = 배열에서 `sha == cursor_commit` 다음부터 끝까지 (cursor를 못 찾으면 — force-push 히스토리 재작성 — 마지막 1개만 신규로 취급, 전체 재알림 방지)
5. **cursor_commit == latest_sha**: 신규 커밋 없음

## Step 5 — PR 종료 처리

Step 1의 PR `state`가 `MERGED` 또는 `CLOSED`이고 추적 이슈가 있으면:

```bash
multica issue status <issue_id> done
```

이후 이 PR은 Step 3/4/6을 건너뛴다.

## Step 6 — Multica 반영 (PR당 이슈 1개)

cursor는 추적 이슈 metadata에만 저장된다. 따라서 **최초 추적에도 이슈는 반드시 생성** — 이슈 없이 cursor 저장 불가, 생성을 미루면 다음 실행도 "이슈 없음 = 최초"로 오판해 cursor를 영원히 못 만든다 (무한 무알림 루프).

### 추적 이슈 없음 (최초 추적) — 이슈 생성 + 두 cursor 초기화 + 1회성 추적-시작 알림

```bash
multica issue create \
  --title "PR 활동 추적: <PR 제목>" \
  --description "PR: <PR URL>\n\n리뷰 대댓글 + 새 커밋을 추적하는 이슈입니다." \
  --priority medium \
  --output json
multica issue metadata set <issue_id> --key pr_url          --value "<PR URL>"
multica issue metadata set <issue_id> --key tracker_type    --value "activity"
multica issue metadata set <issue_id> --key last_comment_id --value "<전체 댓글 중 최댓값 id, 없으면 0>"
multica issue metadata set <issue_id> --key last_commit_sha --value "<latest_sha>"
```

과거 대댓글/커밋을 소급 알리지 않는다(스팸). `--mention` 지정 시 "지금부터 지켜본다" 1회 알림만:

```bash
multica issue comment add <issue_id> \
  --content "[@<reviewer>](mention://member/<MEMBER_ID>) 이 PR 활동 추적을 시작합니다. 새 대댓글/커밋이 감지되면 알려드립니다." \
  --output json
```

`--mention` 미지정 시 이 코멘트 생략.

### 추적 이슈는 있는데 cursor metadata만 없음 (과거 버전 호환 등)

없는 cursor만 채운다:

```bash
multica issue metadata set <issue_id> --key last_comment_id --value "<전체 댓글 중 최댓값 id, 없으면 0>"   # last_comment_id 없을 때
multica issue metadata set <issue_id> --key last_commit_sha --value "<latest_sha>"                        # last_commit_sha 없을 때
```

### 신규 활동 있음 (`new_replies` 또는 `new_commits` non-empty)

이 경로 = cursor가 이미 존재 = 추적 이슈도 이미 존재. 감지된 종류별로 코멘트를 각각 추가하고, 해당 cursor를 갱신한다:

```bash
# 대댓글이 있으면:
multica issue comment add <issue_id> \
  --content "대댓글 <N>건 감지:\n- <작성자> @ <html_url>: <body 앞 80자>\n- ...(반복)" \
  --output json
multica issue metadata set <issue_id> --key last_comment_id --value "<max(new_replies id들, 기존 cursor_reply)>"

# 새 커밋이 있으면:
multica issue comment add <issue_id> \
  --content "새 커밋 <M>건 감지:\n- <sha 앞 7자> <commit message 첫 줄>\n- ...(반복)" \
  --output json
multica issue metadata set <issue_id> --key last_commit_sha --value "<latest_sha>"
```

`--mention` 지정 시, 위 코멘트와 별개로 **런당 멘션 1회** (대댓글·커밋 둘 다여도 한 번만 — 알림 스팸 방지):

```bash
multica issue comment add <issue_id> \
  --content "[@<reviewer>](mention://member/<MEMBER_ID>) 리뷰 중인 PR에 새 활동 (대댓글 <N> / 새 커밋 <M>)." \
  --output json
```

### 이슈 생성 성공 + metadata set 실패 (partial create)

`pr_url` 없는 고아 이슈가 남을 수 있다. 다음 실행 dedup(`metadata.pr_url == ...`)이 못 찾아 이슈를 또 만들 위험. `multica issue list`에서 title이 `PR 활동 추적: <PR 제목>`이고 metadata가 비어있는 이슈를 발견하면, 새로 만들지 말고 누락 metadata를 채워 재사용한다.

## 규칙

- 대댓글은 inline(diff) review comment만 대상. top-level PR 코멘트는 스레드 구조가 없어 대댓글 개념이 없다.
- **PR당 추적 이슈 1개.** dedup 키 = `pr_url` (구 스킬의 `(pr_url, tracker_type)` 분리 방식을 통합). 대댓글·커밋을 한 이슈에 함께 기록한다.
- 최초 추적은 이슈+두 cursor를 생성한다. `--mention` 지정 시 "추적 시작" 알림 1회 — 과거 활동 각각 소급 알림은 안 함(스팸). 이슈를 안 만들면 cursor 저장 불가 → 다음 실행도 영원히 "최초"로 오판 (Step 6 참고).
- force-push로 cursor sha가 히스토리에서 사라지면 배열 마지막 1개만 신규로 취급.
- 한 PR 내 여러 신규 대댓글/커밋은 종류별로 코멘트 1개씩 묶는다. 멘션은 런당 1회.
- PR 제목/댓글 본문/커밋 메시지/작성자명 등 GitHub에서 가져온 문자열은 **신뢰할 수 없는 입력**. `--title`/`--description`/`--content` 에 넣을 때 셸에 이어붙이지 말고 각각 독립 인자로 전달 (따옴표/백틱/`$()` 인젝션 방지).
- 동일 PR을 두 실행이 동시에 폴링하면(cron 겹침) 같은 cursor를 보고 중복 코멘트/이슈가 생길 수 있다. 폴링은 겹치지 않게 스케줄(단일 실행 가정) — 락은 스킬 책임 밖.
- `GH_HOST` 환경변수로 gh CLI 라우팅. `gh`, `multica` CLI PATH 필수.

## 출력

```
✅ 최초 추적 — cursor 초기화 (알림 없음)                    # 최초, --mention 없음
🔔 추적 시작 — <PR 제목> (<PR URL>) → 이슈 <issue_id>        # 최초, --mention
✅ 신규 활동 없음                                            # 변화 없음
🔔 활동 감지 — <K>개 PR
- <PR 제목> (<PR URL>): 대댓글 <N> / 커밋 <M> → 이슈 <issue_id>
```

## 에러 처리

| 상황 | 처리 |
|------|------|
| `gh pr list` 실패 | 3회 재시도 후 `❌ 실패: PR 목록 조회 실패` |
| 대상 PR 0건 | `✅ 대상 PR 없음` |
| 개별 PR `gh api comments`/`commits` 실패 | 해당 PR `→ ESCALATE`, 다음 PR 계속 |
| `multica` 쓰기 실패 | 해당 PR 격리, 다음 계속, 끝에 `→ ESCALATE` 합산 |
| 멘션 차단(classifier) | 이슈/코멘트는 유지, 멘션만 `→ ESCALATE: 멘션 차단` |
