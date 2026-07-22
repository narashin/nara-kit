---
name: nara-jira-triage
description: >-
  Triage your ready Jira tickets (To Do / Selected) into per-ticket Multica queue issues, classified by type and routed to a repo — ready for you to trigger into a Stage 2 herdr session (human-judged). Also reconciles the queue: closes queue issues whose Jira ticket is already Done. Stage 1 never runs code.
  USE FOR: "jira triage", "지라 트리아지", "내 티켓 큐", "assignee 자동 분류", "완료 티켓 큐 정리", Multica Jira autopilot.
  DO NOT USE FOR: 티켓 생성 (→ slack-to-jira), 버그 원인 분석 (→ /nara-incident).
---

# jira-triage — 내 Jira 티켓 → Multica 작업 큐

내게 할당된 **착수 가능(To Do / Selected for Development)** Jira 티켓을 폴링해 **구현/버그픽스/기획/기타**로 분류하고, **티켓당 Multica 이슈**(UNASSIGNED, status To Do)로 만들어 watching 큐를 채운다.

> **테제 가드:** autopilot은 코드를 실행하지 않는다. 큐만 채운다. 네가 **큐에서 골라 착수 트리거(판단)**하는 순간이 착수 결정(심사) — 그때부터 [Stage 2](#stage-2--착수-네가-트리거)가 돈다.

참조: [Config](references/config.md) (project→repo·ready 상태) · [Issue body](references/issue-body.md) (타입별 큐 이슈 본문) · [Deploy](references/deploy.md) (Multica autopilot + herdr Stage 2 셋업)

## 2-stage 루프

```
[Stage 1] jira-triage 크론(LLM) → ready 티켓 → 티켓당 Multica 이슈(큐, UNASSIGNED) + 멘션
[reconcile] 별도 결정론 스크립트(LLM 아님, out-of-band) → Jira Done된 잔여 큐 이슈 → done 전이
[Stage 2] 너: 큐 판단 → /nara-jira-drain <KEY> → herdr worktree(space=repo@branch)에 Claude Code 세션
          → dev-mode/doc-mode PR까지 (게이트 미달→정지+리포트) · 인터랙티브 $0
[Stage 3] review-queue → PR 리뷰 → 너: merge → herdr worktree cleanup
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

> **reconcile은 이 LLM 파이프라인에 포함 안 됨.** classify(2)만 의미 판단이라 LLM이 필요하고, reconcile은 결정론이라 별도 out-of-band 스크립트로 뺀다 (아래 [reconcile](#reconcile-jira-done--큐-이슈-완료-out-of-band) 참조). 오토파일럿에 얹으면 빈 런마다 LLM 토큰을 낭비하므로 분리.

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
| **버그픽스** | 결함·회귀·보안 누락·오작동 | dev-mode |
| **구현** | 신규 동작·기능·제거·마이그레이션·테스트 추가 | dev-mode |
| **기획** | 타당성·조사·scope·설계·PRD·방법론 — 코드 아님 | doc-mode |
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

dedup: metadata `jira_key` 동일 이슈 존재 → 생성·멘션 스킵. `--dry-run` 이면 Step 6 전체 스킵.

### reconcile (Jira Done → 큐 이슈 완료, out-of-band)

큐를 채우는 방향과 **역방향** sync. 이미 완료된 티켓의 잔여 큐 이슈를 닫아 큐를 최신으로 유지한다. **결정론 — LLM 의미 판단 없음.** classify와 달리 여기엔 추측이 없다: Jira `statusCategory = Done` 은 사람이 이미 내린 완료 결정이고, 이 스텝은 그 결정을 큐에 반영할 뿐이다.

LLM이 필요 없으므로 **오토파일럿(LLM)이 아니라 별도 셸 스크립트 + OS 크론**으로 실행한다 — Jira REST(PAT) + `multica` CLI만 쓴다. 배포·스크립트 상세는 [deploy](references/deploy.md) 참조. 로직:

```bash
# 1. 열린 큐 이슈 수집 — metadata.jira_key 있고 status ∈ {todo, in_progress, in_review, blocked}
multica issue list --output json --limit 100   # metadata 인라인 → jira_key 필터, done/cancelled 제외

# 2. 배치 조회 (한 방). statusCategory=Done 이 done/resolved/closed 전부 포함
curl -sf -G "$JIRA_BASE/rest/api/2/search" -H "Authorization: Bearer $PAT" \
  --data-urlencode "jql=key IN (<수집 KEY들>) AND statusCategory = Done" --data-urlencode "fields=key"

# 3. 매칭된 KEY의 Multica 이슈 → done + 코멘트 (근거 남김)
multica issue status <issue_id> done
multica issue comment add <issue_id> \
  --content "Jira <KEY> Done → 큐 이슈 자동 완료 (reconcile)"
```

- 수집 KEY 0건 또는 Done 매칭 0건 → 조용히 스킵 (no-op) — 스크립트 자체가 게이트라 별도 precheck 불필요
- `--dry-run` 이면 3의 쓰기 전체 스킵, 닫을 대상만 미리보기
- Jira Done = 워크가 랜딩됐다는 신호. 드물게 Stage 2 task in-flight 중 Jira가 먼저 Done이어도 큐 이슈 완료가 맞음 (중복 착수 방지)
- reconcile은 **Multica 이슈** 상태만 바꾼다 — Jira 상태는 절대 건드리지 않음

## Stage 2 — 착수 (네가 트리거)

큐 이슈를 판단 후 `/nara-jira-drain <KEY>` 로 트리거하면 jira-drain 스킬이:
1. 이슈 metadata(`jira_key`/`triage_type`/`repo`/`pr_language`/`sub_repo`) 읽음. `local_path`는 로컬 config(`~/.claude/jira-triage.md`)에서 조회 — 이슈 metadata엔 없음. (`session_group`은 herdr가 무시 — 아래 규칙 참조)
2. `herdr worktree create`로 **space=repo@branch** 워크트리 + claude pane 생성 (herdr엔 group 개념 없음 — space 자체가 티켓 단위)
3. dev-mode(구현/버그픽스) 또는 doc-mode(기획) 프롬프트를 claude 초기 인자로 주입 — **PR까지, 머지 X, 게이트 미달→정지+리포트, PR 언어 프로젝트별**
4. 이슈 → In Progress. 완료 시 PR 링크/정지 사유 코멘트

> 인터랙티브(구독) 실행 = $200 헤드리스 풀 안 씀. 헤드리스는 예산 내 선택적(별도).

## 규칙

- **Stage 1은 코드 실행 금지** — 큐만 채운다. 착수는 사람이 jira-drain 트리거로 결정
- **reconcile은 테제 위반 아님** — Jira Done은 사람이 이미 내린 완료 결정. 큐 이슈 done 전이는 그 결정의 기계적 반영이지 새 착수·판단이 아님 (결정론). 또한 오토파일럿(LLM) 밖 out-of-band 스크립트라 Stage 1 LLM 파이프라인과 무관
- 분류는 summary/description **LLM 의미 판단** — issuetype 필드 기대 안 함
- 큐 대상 = ready 상태(To Do/Selected)만. Backlog·In Progress·Done·컨테이너 제외
- 큐 이슈는 **UNASSIGNED 생성** — autopilot이 자동 착수하지 않음 (사람 게이트)
- dedup = metadata `jira_key`. 스킵 이슈엔 멘션 안 단다
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
| reconcile Jira REST 실패 (스크립트) | 스크립트 die + 로그, 다음 크론 재시도 (오토파일럿 무관) |
| reconcile `multica issue status` 실패 | 해당 이슈 WARN 스킵, 다음 계속 |
