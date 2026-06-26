---
name: jira-triage
description: >-
  Triage your ready Jira tickets (To Do / Selected) into per-ticket Multica queue issues, classified by type and routed to a repo — ready for you to dispatch to a Dev/Planner agent. Never runs code.
  USE FOR: "jira triage", "지라 트리아지", "내 티켓 큐", "assignee 자동 분류", Multica Jira autopilot.
  DO NOT USE FOR: 티켓 생성 (→ slack-to-jira), 버그 원인 분석 (→ /incident).
---

# jira-triage — 내 Jira 티켓 → Multica 작업 큐

내게 할당된 **착수 가능(To Do / Selected for Development)** Jira 티켓을 폴링해 **구현/버그픽스/기획/기타**로 분류하고, **티켓당 Multica 이슈**(UNASSIGNED, status To Do)로 만들어 watching 큐를 채운다.

> **테제 가드:** autopilot은 코드를 실행하지 않는다. 큐만 채운다. 네가 큐에서 골라 **역할 agent에 assign + In Progress**로 바꾸는 순간이 착수 결정(심사) — 그때부터 [Stage 2](#stage-2--착수-네가-트리거)가 돈다.

참조: [Config](references/config.md) (project→repo·ready 상태) · [Issue body](references/issue-body.md) (타입별 큐 이슈 본문) · [Deploy](references/deploy.md) (Multica autopilot + Dev/Planner agent 셋업)

## 2-stage 루프

```
[Stage 1] jira-triage 크론 → ready 티켓 → 티켓당 Multica 이슈(큐, UNASSIGNED)
[Stage 2] 너: 큐에서 골라 Dev/Planner agent에 assign + In Progress
          → agent가 headless Claude Code shell out (네 머신, repo) → PR까지 → 머지 X
[Stage 3] review-reminder/review-queue → PR 리뷰 → 너: merge
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
5. **dedup** — `multica issue list`, metadata `jira_key` 있으면 스킵
6. **emit** — 티켓당 UNASSIGNED 큐 이슈 + 신규에만 멘션

```bash
# Step 1 — poll. ready 상태만 (Backlog/In Progress/Done 제외)
jira_search jql='assignee = currentUser() AND status in ("To Do", "Selected for Development") AND project IN (SANDY, LYRIS) ORDER BY updated DESC' \
  fields='key,summary,status,description,labels,subtasks,parent'   # issuetype 보통 빈값 — 의미로 분류
```

ready 상태 목록은 config `ready_statuses` 로 조정. 폴링 윈도우 없음 — dedup이 재처리 차단.

### classify 스키마

**issuetype 필드는 보통 비어 온다.** summary(+있으면 description)를 LLM이 **의미로 판단**한다.

| 타입 | 판정 (의미 기준) | 착수 agent |
|------|------|------|
| **버그픽스** | 결함·회귀·보안 누락·오작동 | Dev |
| **구현** | 신규 동작·기능·제거·마이그레이션·테스트 추가 | Dev |
| **기획** | 타당성·조사·scope·설계·PRD·방법론 — 코드 아님 | Planner |
| **기타** | 운영·질문·판단 불가 | (무 — 수동) |

모호 → **기타 + `[UNVERIFIED: 분류 모호]`**, 추측 금지.

### subtask 게이트

parent는 epic처럼 컨테이너로 열고 실제 작업은 subtask에 적는 일이 잦다:

- 티켓에 **subtask가 있으면** → parent는 큐에 **안 넣음** (컨테이너). 열린 subtask가 ready 상태면 그게 큐에 (자기 행으로)
- subtask거나 subtask 없으면 → 정상 큐잉
- parent↔자식 중복 흡수

### emit (Multica 큐 이슈)

티켓당 1개, **UNASSIGNED** (네가 나중에 역할 agent에 assign):

```bash
multica issue create \
  --title "[<KEY>] <타입>: <summary>" \
  --description "<이슈 본문 — Issue body 참조>" \
  --priority medium --output json
multica issue metadata set <issue_id> --key jira_key   --value "<KEY>"
multica issue metadata set <issue_id> --key triage_type --value "<타입>"
multica issue metadata set <issue_id> --key repo        --value "<host/owner/repo>"
# --mention 지정 시 신규 이슈에만:
multica issue comment add <issue_id> \
  --content "[@<표시명>](mention://member/<MEMBER_ID>) <KEY> 큐에 추가됨 (<타입>)" --output json
```

dedup: metadata `jira_key` 동일 이슈 존재 → 생성·멘션 스킵. `--dry-run` 이면 Step 6 전체 스킵.

## Stage 2 — 착수 (네가 트리거)

큐 이슈를 **Dev/Planner agent에 assign + status In Progress**로 바꾸면 그 agent의 task가 enqueue된다 (review-reminder의 "assign→자동실행"과 동일 메커닉). agent는:

1. 이슈 metadata에서 `jira_key` / `repo` 읽음
2. bash로 headless Claude Code shell out (네 머신, repo 디렉터리):
   `claude -p "/nara-kit:wt <KEY> → /nara-kit:prep <KEY> → dev-mode(또는 doc-mode)"`
3. **PR까지만. 머지 금지.** dev-mode 내부 게이트(gap<80 등) 미달 시 **강행 말고 멈춰 이슈에 리포트**
4. PR 링크를 이슈 코멘트로 남기고 done → Stage 3(PR 리뷰 루프)로 인계

> Stage 2 agent/실행 환경 셋업은 [Deploy](references/deploy.md). agent 런타임 전제: 네 머신에 `git`·`claude` CLI + repo + creds.

## 규칙

- **Stage 1은 코드 실행 금지** — 큐만 채운다. 착수는 사람이 assign으로 결정
- 분류는 summary/description **LLM 의미 판단** — issuetype 필드 기대 안 함
- 큐 대상 = ready 상태(To Do/Selected)만. Backlog·In Progress·Done·컨테이너 제외
- 큐 이슈는 **UNASSIGNED 생성** — autopilot이 agent에 자동 assign하지 않음 (사람 게이트)
- dedup = metadata `jira_key`. 스킵 이슈엔 멘션 안 단다
- `--dry-run` 이면 Multica 쓰기 전체 스킵
- config에 비밀값 없음 — Jira 인증은 MCP 레이어

## 오류 처리

| 상황 | 처리 |
|------|------|
| `jira_search` 실패 | 3회 재시도 후 `❌ 실패: Jira 조회 실패` |
| 조회 0건 | `✅ 신규 ready 티켓 없음` |
| project repo 매핑 없음 | 큐 이슈는 생성하되 `[UNVERIFIED: repo 매핑 없음]` (Dev assign 전 수동 확인) |
| `multica issue create` 실패 | 해당 티켓 격리, 다음 계속, `→ ESCALATE` |
| 멘션 차단 (classifier) | 이슈는 생성, 멘션만 `→ ESCALATE: 멘션 차단` |
