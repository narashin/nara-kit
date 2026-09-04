---
name: nara-jira-triage
description: >-
  Triage ready Jira tickets (To Do / Selected) into per-ticket Multica queue issues — classified, repo-routed, human-judged before Stage 2. Creation only: reverse status sync (merged PR → queue done) is a cron script whose contract this skill declares. Stage 1 never runs code.
  USE FOR: "jira triage", "지라 트리아지", "내 티켓 큐", "assignee 자동 분류", "큐 상태 정리", Multica Jira autopilot.
  DO NOT USE FOR: 티켓 생성 (→ slack-to-jira), 버그 원인 분석 (→ /nara-incident).
---

# jira-triage — 내 Jira 티켓 → Multica 작업 큐

내게 할당된 **착수 가능(To Do / Selected for Development)** Jira 티켓을 폴링해 **구현/버그픽스/기획/기타**로 분류하고, **티켓당 Multica 이슈**(UNASSIGNED, status To Do)로 만들어 watching 큐를 채운다.

> **테제 가드:** autopilot은 코드를 실행하지 않는다. 큐만 채운다. 네가 **큐에서 골라 착수 트리거(판단)**하는 순간이 착수 결정(심사) — 그때부터 [Stage 2](#stage-2--착수-네가-트리거)가 돈다.

참조: [Config](references/config.md) (project→repo·ready 상태) · [Issue body](references/issue-body.md) (타입별 큐 이슈 본문) · [Deploy](references/deploy.md) (Multica autopilot + herdr Stage 2 셋업)

## 2-stage 루프

```
[Stage 1] jira-triage 크론 → ready 티켓 → 티켓당 Multica 이슈(큐, UNASSIGNED) + 멘션
[Stage 2] 너: 큐 판단 → /nara-jira-drain <KEY> → herdr worktree(space=repo@branch)에 Claude Code 세션
          → 구현/기획 흐름으로 PR까지 (게이트 미달→정지+리포트) · 인터랙티브 $0
[Stage 3] review-queue → PR 리뷰 → 너: merge → herdr worktree cleanup
          ↳ cleanup 안 돌아도 다음 Stage 1 실행의 Step 7 reconcile이 머지 PR 보고 큐를 done으로 되돌린다
```

사람 게이트 2곳: **착수 선택** + **merge**.

## 인자 (`$ARGUMENTS`)

```
jira-triage [--assignee <currentUser|ACCOUNT_ID>] [--projects <KEY,KEY>] [--mention <MEMBER_ID>] [--dry-run]
```

| 인자 | 기본값 | 설명 |
|------|--------|------|
| `--assignee` | `currentUser()` | autopilot jira MCP가 본인 토큰 인증 시 = 나 |
| `--projects` | config 매핑 전체 key | 폴링할 project 화이트리스트 |
| `--mention` | (없음) | Multica member UUID. **신규 큐 이슈에만** 멘션 → 알림 |
| `--dry-run` | false | Multica 쓰기 없이 분류·큐 미리보기만 |

## 파이프라인

1. **poll** — ready 상태 할당 티켓 조회
2. **classify** — 구현 \| 버그픽스 \| 기획 \| 기타 (summary/description 의미 판단)
3. **subtask 게이트** — 컨테이너(subtask 보유)는 제외, 실제 작업 단위만
4. **route** — project key → repo ([Config](references/config.md))
5. **dedup** — `multica issue list --metadata "jira_key=<KEY>"` (서버측 필터), 결과 있으면 스킵
6. **emit** — 티켓당 UNASSIGNED 큐 이슈 + 신규에만 멘션

Step 1~6은 **생성만** 한다. 미종료 큐 이슈를 PR/Jira 실측으로 되돌리는 건 out-of-band 크론 담당 — [Step 7](#step-7--reconcile-역방향-상태-동기화).

```bash
# Step 1 — poll. ready 상태만 (Backlog/In Progress/Done 제외)
jira_search jql='assignee = currentUser() AND status in ("To Do", "Selected for Development") AND project IN (SVC, APP) ORDER BY updated DESC' \
  fields='key,summary,status,description,labels,subtasks,parent'   # issuetype 보통 빈값 — 의미로 분류
```

ready 상태 목록은 config `ready_statuses` 로 조정. 폴링 윈도우 없음 — dedup이 재처리 차단.

### classify 스키마

**issuetype 필드는 보통 비어 온다.** summary(+있으면 description)를 LLM이 **의미로 판단**한다.

| 타입 | 판정 (의미 기준) | 착수 트랙 |
|------|------|------|
| **버그픽스** | 결함·회귀·보안 누락·오작동 | 구현 흐름 |
| **구현** | 신규 동작·기능·제거·마이그레이션·테스트 추가 | 구현 흐름 |
| **기획** | 타당성·조사·scope·설계·PRD·방법론 — 코드 아님 | 기획 흐름 |
| **기타** | 운영·질문·판단 불가 | 수동 |

모호 → **기타 + `[UNVERIFIED: 분류 모호]`**, 추측 금지.

### APP FE/BE 판정

APP 구현/버그픽스는 sub-repo를 정한다:
- `[FE]` 말머리 또는 UI/컴포넌트/프론트 내용 → **fe** (app-fe, session_group app-fe)
- `[BE]`/`[API]` 또는 서버/엔드포인트/DB 내용 → **be** (app-be, session_group app-be)
- 모호 → 본문에 `[그룹 확인 필요: FE/BE 불명]` 표기, 사람이 트리거 시 선택 (자동 추측 금지)

SVC는 항상 default repo. 기획/기타는 sub-repo 무관.

### subtask 게이트

parent는 epic처럼 컨테이너로 열고 실제 작업은 subtask에 적는 일이 잦다:

- 티켓에 **subtask가 있으면** → parent는 큐에 **안 넣음** (컨테이너). 열린 subtask가 ready 상태면 그게 큐에 (자기 행으로)
- subtask거나 subtask 없으면 → 정상 큐잉
- parent↔자식 중복 흡수

### emit (Multica 큐 이슈)

티켓당 1개, **UNASSIGNED** (네가 나중에 jira-drain으로 트리거):

```bash
multica issue create \
  --title "[<KEY>] <타입>: <summary>" \
  --description "<이슈 본문 — Issue body 참조>" \
  --priority medium --output json
multica issue metadata set <issue_id> --key jira_key      --value "<KEY>"
multica issue metadata set <issue_id> --key triage_type  --value "<타입>"
multica issue metadata set <issue_id> --key repo          --value "<host/owner/repo>"
multica issue metadata set <issue_id> --key session_group --value "<group>"
multica issue metadata set <issue_id> --key pr_language   --value "<ko|en>"
multica issue metadata set <issue_id> --key sub_repo      --value "<default|fe|be>"
# --mention 지정 시 신규 이슈에만:
multica issue comment add <issue_id> \
  --content "[@<표시명>](mention://member/<MEMBER_ID>) <KEY> 큐에 추가됨 (<타입>)" --output json
```

dedup: `multica issue list --metadata "jira_key=<KEY>"` 결과 있으면 생성·멘션 스킵. `--dry-run` 이면 Step 6 전체 스킵.

**전체 목록을 훑어 비교하지 말 것.** `multica issue list`는 100건에서 잘리고(`has_more: true`) 오래된 이슈가 조회 창 밖으로 밀린다. 워크스페이스가 100건을 넘은 시점(2026-09-04 실측)부터 이미 처리한 티켓이 **다시 큐에 들어간다**. metadata 필터는 서버가 걸러 창과 무관하다.

## Step 7 — reconcile (역방향 상태 동기화)

큐는 채워지기만 하고 되돌아오지 않는다 — 큐 `done` 전이는 jira-drain cleanup에만 있고 그건 사람이 herdr space를 정리할 때만 돈다. cleanup 미실행 건·큐 밖 손PR 건은 머지 뒤에도 `in_review`에 박제된다.

**이 스킬은 reconcile을 실행하지 않는다.** 순수 결정론(`gh`/`jq`/`multica`, LLM 판단 0)이라 out-of-band 셸 스크립트 + OS 크론이 담당한다 — 오토파일럿(헤드리스 claude)에 얹으면 빈 런마다 토큰만 태운다. 역할 분리는 고정:

| 주체 | 책임 |
|---|---|
| 오토파일럿(이 스킬 Step 1~6) | **없는 큐 이슈 생성**만 (classify에 LLM 필요) |
| `jira-reconcile.sh` (크론) | **있는 큐 이슈 상태 sync**만. 생성 안 함 |

스크립트가 지키는 전이 계약 (Pass A = PR 실측 우선, Pass B = Jira 미러, Pass C = Jira 역기록):

| 근거 | 전이 | 부수 write |
|---|---|---|
| A. strict 매칭 `MERGED` 1건 | → `done` | `drain_state=done` · `pr_url` |
| A. `MERGED` 0 + `OPEN` 1건 | `todo`\|`in_progress` → `in_review` | `pr_url` |
| A. `MERGED` 2건+ / 매칭 0건 / `CLOSED`만 | 무변경 | 경고 로그 (종료 심사는 사람) |
| B. Jira statusCategory `done` | → `done` | — |
| B. Jira `indeterminate` | `todo` → `in_progress` | `drain_state=manual` |
| C. A가 `done` 처리 + Jira assignee == 나 + Jira가 아직 done 카테고리 아님 | **Jira** → `$JIRA_CLOSE_STATUSES` 첫 매칭 | — (기본 OFF) |

- **PR이 Jira보다 강한 증거** — Pass A 먼저. Jira 쪽이 밀려 있는 게 보통이다
- `gh pr list --search`는 fuzzy(`PROJ-40` 질의에 PROJ-39·29도 온다) → `headRefName`\|`title`에 KEY가 **단어 경계**로 박힌 것만 채택: `(^|[^A-Za-z0-9])<KEY>([^0-9]|$)` (`PROJ-4` ≠ `PROJ-40`)
- **`metadata.pr_url`은 근거 아님** — review-reminder가 KEY 검증 없이 심어 딴 티켓 PR이 붙기도 한다(실제 발생). strict 매칭 결과로 덮어씀
- **Pass B의 `in_progress` 미러는 `drain_state=manual`을 함께 박는다** — 보드에서 카드를 `in_progress`로 옮기는 행위가 곧 착수 지시이고 `multica-dispatch.py`(크론)가 그걸 보고 워커를 띄운다. 미러는 "이미 다른 데서 손으로 하고 있다"는 뜻이라 그대로 두면 두 번째 워커가 붙는다. 착수 판별식은 `in_progress` + `jira_key` 있음 + `drain_state` **없음**
- **Pass C가 유일한 외부 mutation이고 기본 OFF** — 팀이 보는 Jira라 `JIRA_SYNC=1` 로 명시 opt-in 해야 돈다. 켜더라도 가드 2중: assignee가 나인 티켓만, 그리고 Pass A의 `MERGED` 1건 분기에서만 호출. 현재 Jira 상태는 사람이 직접 관리
- **종료 상태명은 프로젝트마다 다르다** — 전이 id 하드코딩 금지. `to.statusCategory.key == "done"` 인 전이 중 `$JIRA_CLOSE_STATUSES`(기본 `Closed,Done,Resolved`) 순서로 첫 매칭을 고른다. 어떤 프로젝트는 `Closed`, 다른 프로젝트는 `Done` 하나뿐 — 이름 하나로 고정하면 한쪽이 통째로 막힌다
- Pass C 실패(PAT 권한 없음·해당 전이 미노출)는 경고 로그만 남기고 진행한다. Jira는 손대지 않은 상태로 남는다

## Stage 2 — 착수 (네가 트리거)

큐 이슈를 판단 후 `/nara-jira-drain <KEY>` 로 트리거하면 jira-drain 스킬이:
1. 이슈 metadata(`jira_key`/`triage_type`/`repo`/`pr_language`/`sub_repo`) 읽음. `local_path`는 로컬 config(`~/.claude/jira-triage.md`)에서 조회 — 이슈 metadata엔 없음. (`session_group`은 herdr가 무시 — 아래 규칙 참조)
2. `herdr worktree create`로 **space=repo@branch** 워크트리 + claude pane 생성 (herdr엔 group 개념 없음 — space 자체가 티켓 단위)
3. 구현(버그픽스 포함) 또는 기획 프롬프트를 claude 초기 인자로 주입 — **PR까지, 머지 X, 게이트 미달→정지+리포트, PR 언어 프로젝트별**
4. 이슈 → In Progress. 완료 시 PR 링크/정지 사유 코멘트

> 인터랙티브(구독) 실행 = $200 헤드리스 풀 안 씀. 헤드리스는 예산 내 선택적(별도).

## 규칙

- **Stage 1은 코드 실행 금지** — 큐만 채운다. 착수는 사람이 jira-drain 트리거로 결정
- 분류는 summary/description **LLM 의미 판단** — issuetype 필드 기대 안 함
- 큐 대상 = ready 상태(To Do/Selected)만. Backlog·In Progress·Done·컨테이너 제외
- 큐 이슈는 **UNASSIGNED 생성** — autopilot이 자동 착수하지 않음 (사람 게이트)
- dedup = metadata `jira_key`. 스킵 이슈엔 멘션 안 단다
- **상태 되돌리기(reconcile)는 이 스킬이 실행하지 않는다** — 결정론이라 크론 스크립트 소유(§Step 7). 여기선 계약만 선언
- 큐 상태 SoT = PR 실측 > Jira 상태 > `pr_url` metadata(오염 가능, 근거 아님) 순
- `--dry-run` 이면 Multica 쓰기 전체 스킵
- config에 비밀값 없음 — Jira 인증은 MCP 레이어
- APP는 FE/BE 판정해 sub-repo 라우팅. 모호하면 사람이 선택 (자동 추측 금지)
- `session_group` metadata는 **legacy** — Stage 2가 herdr로 이관된 뒤(space=repo@branch가 group 역할) jira-drain은 이를 **무시**한다. 하위 호환/참고용으로만 남김 (라우팅은 `repo`+`sub_repo`가 결정)
- 이슈 본문에 타입별 접근법 + 라우팅(repo/sub_repo/PR언어) 기재 — Stage 2 입력

## 오류 처리

| 상황 | 처리 |
|------|------|
| `jira_search` 실패 | 3회 재시도 후 `❌ 실패: Jira 조회 실패` |
| 조회 0건 | `✅ 신규 ready 티켓 없음` |
| project repo 매핑 없음 | 큐 이슈는 생성하되 `[UNVERIFIED: repo 매핑 없음]` (트리거 전 수동 확인) |
| `multica issue create` 실패 | 해당 티켓 격리, 다음 계속, `→ ESCALATE` |
| 멘션 차단 (classifier) | 이슈는 생성, 멘션만 `→ ESCALATE: 멘션 차단` |
| 큐 상태가 실제와 어긋남 (머지됐는데 `in_review` 등) | 이 스킬 소관 아님 — reconcile 크론(§Step 7) 담당. 즉시 필요하면 스크립트 수동 실행 |
