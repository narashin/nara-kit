---
name: nara-wip-sweep
description: >-
  Sweep assigned Jira tickets stuck in an in-progress status, classify each by
  what evidence says actually happened, and report candidates for cleanup — never
  transitioning a ticket itself.
  USE FOR: "In Progress 정리", "진행 중인데 안 하는 티켓", "wip 쓸어내", "티켓 상태 정리",
  "내 In Progress 몇 개야", "wip-sweep".
  DO NOT USE FOR: 큐 채우기 (→ nara-jira-triage), 보드 상태 미러 (→ jira-reconcile 스크립트),
  요구사항 로컬화 (→ nara-prep), 구현 (→ nara-implement).
---

# nara-wip-sweep

"In Progress"가 실제 진행을 뜻하지 않게 된 티켓을 한 번에 쓸어내 분류한다.

동시에 35건을 진행할 수는 없다. 그 숫자는 작업량이 아니라 **상태 부채**다. 착수했다가 놓은 것, 사실상 끝난 것, 애초에 착수할 수 없던 것이 한 상태에 섞여 있으면 어떤 브리핑도 "오늘 무엇부터"를 답할 수 없다.

## 이 스킬이 하지 않는 것

**티켓을 전이시키지 않는다.** 팀이 보는 Jira이고, 상태를 바꾸는 것은 "이 일을 안 한다"는 선언이다. 이 스킬은 근거와 분류만 내놓고 사람이 판정한다. 자동 전이가 필요하면 그건 별개 결정이며 `jira-reconcile.sh`의 `JIRA_SYNC` 게이트가 그 자리다.

## 입력

인자 없음. 대상은 `assignee = currentUser() AND status = "In Progress"`.

| 인자 | 기본값 | 의미 |
|---|---|---|
| `--project <KEY>` | 전체 | 한 프로젝트만 |
| `--limit <N>` | 100 | 조회 상한 |

## 절차

1. **수집** — Jira에서 대상 티켓을 `key,summary,description,status,updated,created,subtasks,parent,labels`로 조회한다.
2. **증거 수집** — 티켓당 아래를 **실측**한다. 추측 금지.
   - `gh pr list --repo <repo> --search <KEY> --state all`, 단어 경계 매칭(`(^|[^A-Za-z0-9])KEY([^0-9]|$)`)으로 필터. `gh pr list --search`는 fuzzy해서 `PROJ-4` 질의에 `PROJ-40`이 온다.
   - subtask 보유 여부 (컨테이너인지)
   - 마지막 갱신 이후 경과일
3. **분류** — 증거로 판정한다. 근거 없는 칸은 `[UNVERIFIED: <이유>]`.

| 분류 | 판정 근거 |
|---|---|
| **사실상 종료** | 단어 경계 매칭 `MERGED` PR 1건 이상 |
| **리뷰 대기** | `OPEN` PR 존재 |
| **컨테이너** | subtask 보유 — 부모는 상태를 가질 자격이 없다 |
| **착수 불가** | 본문에 요구사항·AC가 없어 지금 시작할 수 없다 |
| **방치** | PR 없음 + 마지막 갱신 30일 초과 |
| **진행 중** | 위 어디에도 안 걸림. 실제로 하고 있을 가능성 |

4. **보고** — 실행한 디렉터리에 `wip-sweep.md`로 쓴다. 티켓당 한 줄: 키, 분류, 근거(PR 번호·경과일·빠진 것), 제안 행동. **repo의 `docs/`에 넣지 않는다** — 이건 내 Jira 상태 보고서이고 여러 프로젝트를 걸치므로 어느 repo의 내용도 아니다.
5. **정지** — 여기서 끝이다. 전이는 사람이 한다.

## 출력 형식

```markdown
# WIP Sweep — YYYY-MM-DD

대상 N건 (assignee=나, status=In Progress)

## 사실상 종료 (N)
| 티켓 | 근거 | 제안 |
|---|---|---|
| PROJ-12 | PR #340 merged 2026-07-02 | Done 전이 |

## 착수 불가 (N)
| 티켓 | 빠진 것 | 제안 |
|---|---|---|
| PROJ-3 | 제목만, 본문·AC 없음 | To Do로 되돌리고 AC 보완 |
```

분류가 빈 경우 그 절은 생략하지 않고 `없음`으로 남긴다. 없다는 사실도 정보다.

## 규칙

- **전이 금지.** 제안만. 이 스킬이 `jira_transition_issue`를 호출하는 일은 없다
- 증거 없는 분류 금지. PR을 못 찾았으면 "PR 없음"이 아니라 조회가 실패했을 수 있다 — 실패는 실패로 적는다
- `MERGED` 2건 이상이면 모호로 남긴다. 종료 심사는 사람이 한다
- `metadata.pr_url` 같은 캐시된 링크를 근거로 쓰지 않는다. 키 검증 없이 심어져 딴 티켓 PR이 붙은 사례가 있다
- 30일 임계는 관례일 뿐이다. 경과일을 함께 적어 사람이 다시 판단할 수 있게 한다
- 한 번 쓰고 버리는 잡이다. 정기 스케줄에 얹지 않는다 — 부채가 다시 쌓였을 때 사람이 부른다

## 오류 처리

| 상황 | 처리 |
|---|---|
| Jira 조회 실패 | 중단. 부분 결과로 정리 판단을 하게 만들지 않는다 |
| `gh` 미인증/부재 | PR 증거 없이 진행하되 모든 행에 `[UNVERIFIED: gh 사용 불가]` |
| repo 매핑 없음 | 그 티켓만 `[UNVERIFIED: repo 불명]`, 나머지는 계속 |
