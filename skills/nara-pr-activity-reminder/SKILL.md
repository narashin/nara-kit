---
name: nara-pr-activity-reminder
description: >-
  Record PR activity — replies to your review comments, commits pushed, comments left on your own PR — onto the Multica card that already owns that PR. Creates no cards.
  USE FOR: "내 리뷰에 대댓글", "리뷰 중인 PR에 새 커밋", "내 PR에 누가 코멘트 달았나", "PR 활동 알림", "review activity reminder".
  DO NOT USE FOR: 미리뷰 PR 탐지 (→ nara-review-reminder), 실제 리뷰 작성 (→ nara-code-review / nara-pr-review), 리뷰 큐 드레인 (→ nara-review-queue).
metadata:
  nara:
    scope: multica
---

# nara-pr-activity-reminder — PR 활동 기록

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

지정된 레포의 열린 PR을 폴링해 새 활동을 감지하고, **그 PR을 이미 들고 있는 카드에 코멘트로 적는다.** 카드를 만들지 않는다. `nara-review-reminder`(미리뷰 PR 탐지)의 형제 스킬.

> **이 로직은 100% 결정론 — classify/의미 판단이 전혀 없다** (gh api 조회 + cursor 비교 + multica 쓰기뿐). 따라서 **헤드리스 LLM 오토파일럿이 아니라 out-of-band 셸/스크립트 크론으로 실행**하는 것이 정석 — 빈 런 LLM 토큰 낭비도, codex inactivity 타임아웃도 없다. 이 파일은 그 스크립트의 **로직 스펙**이다 (참조 구현: `gh` + `multica` CLI + cursor).
>
> 오토파일럿과 크론을 **동시에** 돌리지 말 것. 실측으로 그 상태가 6주간 유지됐고, author 가드가 없는 오토파일럿 쪽이 내 PR에도 추적 카드를 만들었다. 크론으로 옮길 때 오토파일럿을 반드시 정지한다.

## 인자 (`$ARGUMENTS`)

```
nara-pr-activity-reminder --host <GH_HOST> --repo <OWNER/REPO> --reviewer <USERNAME> [--mention <MEMBER_ID>]
```

| 인자 | 예시 | 설명 |
|------|------|------|
| `--host` | `github.com` | GitHub 호스트 (기본: `github.com`) |
| `--repo` | `org/repo` | 대상 레포 (`OWNER/REPO`) |
| `--reviewer` | `alice` | 내 username (카드 선택·활동 판별 기준) |
| `--mention` | `<MEMBER_ID>` | (선택) Multica member UUID. 지정 시 신규 활동 감지 때마다 멘션 코멘트 발송 |

인자 없으면 agent instructions에서 주입된 기본값 사용. 그것도 없으면 오류 안내 후 중단.

## PR 한 건 = 카드 한 장

누가 PR을 열었느냐가 대상 카드와 "무엇이 활동인가"를 동시에 정한다.

| PR | 대상 카드 | 활동 | 닫는 주체 |
|----|-----------|------|-----------|
| 내가 연 것 | 작업 카드 (`tracker_type` 없음, `jira_key` 있음) | **남이 단 인라인 코멘트** (대댓글만이 아니라 전부) | `jira-reconcile` — PR 머지 시 |
| 남이 연 것 | 판정 카드 (`tracker_type=review`) | 내 코멘트에 달린 **대댓글** + 저자가 push한 **새 커밋** | `nara-review-reminder` reconcile — PR 머지·클로즈 시 |
| 둘 다 없음 | — | — | — |

**셋째 줄이 이 스킬의 핵심 계약이다.** 판정 카드가 없다는 건 `nara-review-reminder`가 이미 "이 PR은 내 리뷰 대상이 아니다"라고 판단했다는 뜻이다 — `cancelled` 카드는 "무시하라"이고, 그쪽 dedup은 상태를 안 보므로 재생성되지 않는다. 여기서 카드를 새로 만들면 그 판단을 손으로 뒤집는 것이다. **로그만 남기고 건너뛴다.**

활동 종류가 갈리는 이유도 같은 자리에 있다. 내 PR에서는 커밋이 내 것이라 알리면 내 push에 내가 알림을 받고(실제로 그랬다), 정작 중요한 신호인 "리뷰어가 처음 남긴 코멘트"는 아무에게도 답글이 아니라서 대댓글 필터에 안 걸린다. 남의 PR에서는 반대다 — 그 PR의 모든 인라인 코멘트가 남의 코드 얘기라 "누가 코멘트 달았다"는 소식이 아니고, "내 말에 답했다"가 소식이다.

**절대 안 하는 것:** 카드 생성, 카드 종료, `tracker_type` 쓰기, 판정 카드에 `reviewed` 쓰기(그건 `nara-review-reminder` dedup의 source of truth다).

## Step 1 — 대상 PR 조회 (레포당 한 번)

```bash
GH_HOST=<host> gh pr list \
  --repo <OWNER/REPO> \
  --state open \
  --json number,title,url,state,author,headRefName,reviewRequests,reviews \
  --limit 100
```

`author.login == <reviewer>` 면 **내 PR**. 아니면 아래 중 **하나라도** 만족해야 대상:

1. `reviewRequests[].login` 에 `<reviewer>` 포함
2. `reviews[].author.login` 에 `<reviewer>` 포함

`reviewRequests` 는 **`login` 만 본다** — 팀 요청(`slug`)은 일부러 확장하지 않는다. `nara-review-reminder` 는 확장해야 맞지만(놓치면 리마인더 자체가 없다) 여기서 확장하면 리뷰할 생각도 없는 PR마다 알림이 온다. 팀 요청 건은 내가 실제로 리뷰를 남기는 순간 2번으로 걸리고, 활동이 의미를 갖는 시점도 거기다.

**내가 approve해도 추적은 안 멈춘다.** 이 repo들은 `dismiss_stale_reviews=False` 라서 승인 뒤 push가 와도 승인이 유지되고 재요청도 안 간다. 그 조용한 구간이 정확히 이게 지켜보는 것이다.

## Step 2 — 대상 카드 조회

```bash
multica issue list --metadata "pr_url=<PR URL>" --output json
```

**서버측 `--metadata` 필터로 조회한다.** 이 워크스페이스는 이미 `has_more: true` 를 답하고 정렬이 보드 position이라, 필터 없는 `--limit 100` 창은 찾으려는 행을 조용히 빠뜨린다. `nara-review-reminder` 와 `nara-jira-triage` dedup이 같은 결함을 이미 겪었다.

결과 중 `status` 가 `todo|in_progress|in_review|blocked` 인 것만 대상:

- **내 PR** → `tracker_type` 이 없는 카드
- **남의 PR** → `tracker_type == "review"` 카드

닫힌 카드에는 쓰지 않는다. `done` 은 PR이 끝났거나 reconcile이 정리했다는 뜻이고, `cancelled` 은 내가 "이 PR 무시"라고 정한 것이다.

내 PR인데 카드가 아예 없으면 작업 카드를 하나 만든다 — 브랜치나 제목의 티켓 키로 (`jira_key` + `repo` + `pr_url`, `tracker_type` 없음). 이건 추적 카드가 아니라 `/drain`·`/scan` 이 먹는 보통 작업 카드다. 티켓 키가 없거나 그 키의 카드가 이미 다른 PR을 가리키면 경고만 남기고 만들지 않는다.

## Step 3 — 활동 감지

```bash
GH_HOST=<host> gh api "repos/<OWNER/REPO>/pulls/<PR_NUMBER>/comments" --paginate   # 인라인 review comment
GH_HOST=<host> gh api "repos/<OWNER/REPO>/pulls/<PR_NUMBER>/commits" --paginate    # 남의 PR만
```

커서는 대상 카드 metadata의 `last_comment_id` · `last_commit_sha` 다.

**커서가 없으면(이 카드 첫 패스) 커서만 기록하고 알림은 0건.** 과거분을 소급해 알리지 않는다. 카드를 물려받은 경우 그 이력은 이전 카드에서 이미 한 번 보고됐다.

### 코멘트

`last_comment_id` 는 **정수로 비교한다** — 문자열로 저장돼 있어도 비교·최댓값 계산 전에 정수 변환한다 (자릿수가 늘면 문자열 비교가 틀어진다. `"1000" < "999"`).

- **내 PR**: `user.login != <reviewer>` 이고 `id > cursor` 인 것 전부
- **남의 PR**: 위 조건에 더해 `in_reply_to_id` 가 **내 코멘트 id** 중 하나

둘 다 인라인(diff) review comment만 대상이다. top-level PR 코멘트는 스레드 구조가 없다.

### 커밋 (남의 PR만)

배열은 오래된 순이라 마지막 원소가 최신이다.

1. `latest_sha` == `last_commit_sha` → 신규 없음
2. `last_commit_sha` 가 배열에 있으면 그 다음부터 끝까지가 신규
3. 배열에 없으면(force-push로 히스토리 재작성) **마지막 1개만** 신규로 취급 — 전체 재알림 방지

## Step 4 — 카드에 기록

종류별로 코멘트 1개씩, 해당 커서 갱신:

```bash
multica issue comment add <issue_id> --content "리뷰 코멘트 <N>건 감지:\n- <작성자> @ <html_url>: <본문 앞 80자>\n- ..."
multica issue metadata set <issue_id> --key last_comment_id --value "<신규 중 최댓값 id>"

multica issue comment add <issue_id> --content "새 커밋 <M>건 감지:\n- <sha 앞 7자> <커밋 메시지 첫 줄>\n- ..."
multica issue metadata set <issue_id> --key last_commit_sha --value "<latest_sha>"
```

내 PR이면 첫 코멘트의 라벨이 `리뷰 코멘트`, 남의 PR이면 `대댓글` 이다.

`--mention` 지정 시 위와 **별개로 런당 멘션 1회** (두 종류 다 감지돼도 한 번만 — 알림 스팸 방지):

```bash
multica issue comment add <issue_id> \
  --content "[@<reviewer>](mention://member/<MEMBER_ID>) <내 PR|리뷰 중인 PR>에 새 활동 (<요약>)."
```

## 규칙

- **PR당 카드 1장.** 이 스킬은 그 카드를 고르는 쪽이지 만드는 쪽이 아니다.
- 카드 본문(description)은 건드리지 않는다. 사람이 손댔을 수 있다. 기록은 코멘트로만.
- 대상 카드가 없으면 **로그만 남기고 다음 PR로**. 조용히 넘어가면 "아무 일도 안 일어남"과 구분이 안 되고, 원인 둘(reconcile이 닫았다 / 내가 취소했다)의 대응이 다르다.
- PR 제목·댓글 본문·커밋 메시지·작성자명 등 GitHub에서 온 문자열은 **신뢰할 수 없는 입력**. `--content` 등에 넣을 때 셸에 이어붙이지 말고 독립 인자로 전달 (따옴표/백틱/`$()` 인젝션 방지).
- 코멘트 본문은 개행을 접어 한 줄로 만든 뒤 자른다. 안 그러면 여러 줄 코멘트 하나가 불릿 목록을 깨뜨린다.
- 같은 PR을 두 실행이 동시에 폴링하면(cron 겹침) 같은 커서를 보고 중복 코멘트가 생긴다. 겹치지 않게 스케줄한다 — 락은 이 스킬 책임 밖.
- **카드를 `in_progress`로 옮기면 재리뷰 요청이다** (판정 카드 한정). 판정 후 `in_review` 로 돌아오므로 라운드마다 다시 쓸 수 있다. 새 커밋 감지로 자동 발동하는 일은 없다. 계약: [review-card-link](references/review-card-link.md).
- `GH_HOST` 환경변수로 gh CLI 라우팅. `gh`, `multica` CLI PATH 필수.

## 출력

```
✅ 신규 활동 없음
🔔 활동 감지 — <K>개 PR
- <PR 제목> (<PR URL>): 리뷰 코멘트 <N>  →  <카드 ident>          # 내 PR
- <PR 제목> (<PR URL>): 대댓글 <N> / 커밋 <M>  →  <카드 ident>     # 남의 PR
⚠️ 카드 없어 건너뜀 — <PR URL>
```

## 에러 처리

| 상황 | 처리 |
|------|------|
| `gh pr list` 실패 | 3회 재시도 후 `❌ 실패: PR 목록 조회 실패` |
| 대상 PR 0건 | `✅ 대상 PR 없음` |
| 개별 PR `gh api comments`/`commits` 실패 | 해당 PR `→ ESCALATE`, 다음 PR 계속 |
| 카드 조회 실패 | 해당 PR 건너뜀 (없는 것으로 오판해 만들지 않는다 — 애초에 만들지 않으므로 안전) |
| `multica` 쓰기 실패 | 해당 PR 격리, 다음 계속, 끝에 `→ ESCALATE` 합산 |
| 멘션 차단(classifier) | 기록 코멘트는 유지, 멘션만 `→ ESCALATE: 멘션 차단` |
