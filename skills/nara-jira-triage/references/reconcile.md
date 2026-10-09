# reconcile: 큐 이슈 상태 동기화 계약

큐는 채워지기만 하고 되돌아오지 않는다. 카드가 만들어진 뒤 PR이 열리고 머지되고 Jira 상태가 바뀌어도 이 스킬은 그 카드를 다시 보지 않는다(dedup이 건너뛴다). 그 뒤를 맡는 것이 `jira-reconcile.sh`다. 순수 결정론이라 오토파일럿에 얹지 않고 셸 스크립트 + OS 크론으로 돈다.

이 문서는 스크립트가 지키는 계약이다. 스크립트 자체는 이 repo에 없다(사내 호스트와 식별자가 박혀 있어 private 쪽에 둔다).

## 원칙

- 보드는 Jira의 거울이다. 큰 칸은 Jira가 정하고, 그 안의 세부 단계(리뷰 중, 막힘)는 PR과 판정에서 계산한다. 손으로 옮기는 상태는 없다
- **PR이 Jira보다 강한 증거다.** PR 패스가 먼저 돌고 Jira가 그 결과를 따라온다
- 큐 상태 SoT 순서: PR 실측 > Jira 상태 > `pr_url` metadata(오염 가능, 근거 아님)

## 전이 계약

| 패스 | 근거 | 카드 전이 | 부수 write |
|---|---|---|---|
| A. PR → 카드 | strict 매칭 `MERGED` 1건 | → `done` | `drain_state=done` · `pr_url` |
| A | `MERGED` 0 + draft 아닌 `OPEN` 1건 | `todo`\|`in_progress` → `in_review` | `pr_url` |
| A | `MERGED` 2건+ / 매칭 0건 / `CLOSED`만 / draft만 | 무변경 | 경고 로그 (종료 심사는 사람) |
| B. Jira → 카드 | Jira statusCategory `done` | → `done` | 없음 |
| B | Jira 상태가 `$JIRA_REVIEW_STATUSES` 중 하나 | `todo`\|`in_progress` → `in_review` | 없음 |
| B | Jira `indeterminate` | `todo` → `in_progress` | `drain_state=manual` |
| B | Jira `new` (To Do) | `in_progress` + `drain_state=manual` → `todo` | `drain_state` 삭제 |
| C. PR → Jira | A의 `MERGED` 1건 | **Jira** → `$JIRA_CLOSE_STATUSES` 첫 매칭 | 없음 |
| C | A의 `OPEN` 1건 (카드가 `in_review`가 된 뒤에도 매 회차) | **Jira** → `$JIRA_REVIEW_STATUSES` 첫 매칭 | 없음 |
| D. 판정 해제 | `blocked` + `triage_block` 있음 + `drain_state` 없음 + Jira 본문·코멘트 변경 | → `todo` | `triage_block`·`triage_block_hash` 삭제 |

## 패스별 주의

**A. PR 매칭.** `gh pr list --search`는 fuzzy다(`PROJ-40` 질의에 PROJ-39·29도 온다). `headRefName`\|`title`에 KEY가 **단어 경계**로 박힌 것만 채택한다: `(^|[^A-Za-z0-9])<KEY>([^0-9]|$)` (`PROJ-4` ≠ `PROJ-40`). `metadata.pr_url`은 근거가 아니다. KEY 검증 없이 심긴 적이 있어 strict 매칭 결과로 덮어쓴다. draft PR은 아직 쓰는 중이라 리뷰 중으로 치지 않는다.

**B. `in_progress` 미러는 `drain_state=manual`을 함께 박는다.** 미러는 "이미 다른 데서 손으로 하고 있다"는 뜻이고, 착수 실행기는 이 표시를 보고 `/drain`을 거부한다. Jira가 To Do로 되돌아가면 표시도 지운다. 남겨두면 그 뒤의 `/drain`이 계속 거부된다. 워커가 붙어 있는 카드(`drain_state=dispatched`)는 Jira가 To Do여도 되돌리지 않는다. 그건 어긋남이 아니라 진짜 작업이다.

**C. Jira 되쓰기는 기본 ON이다.** 이 스크립트가 하는 유일한 외부 mutation이라 가드가 둘 걸린다: assignee가 나인 티켓만, 그리고 이미 done 카테고리인 티켓은 건드리지 않는다(열린 PR이 닫힌 티켓을 다시 열면 안 된다). 회차 단위로 끄려면 `JIRA_SYNC=0`.

- **상태명은 프로젝트마다 다르다.** 전이 id 하드코딩 금지. 종료는 `to.statusCategory.key == "done"`인 전이 중 `$JIRA_CLOSE_STATUSES`(기본 `Closed,Done,Resolved`) 순서로 첫 매칭, 리뷰는 `indeterminate`인 전이 중 `$JIRA_REVIEW_STATUSES`(기본 `In Review`)의 첫 매칭을 고른다
- **리뷰 상태가 없는 워크플로는 정상이다.** 그 프로젝트의 Jira는 In Progress에 머물고 리뷰 단계는 카드에만 있다. 경고를 남기지 않는다
- 실패(PAT 권한 없음, 전이 미노출)는 경고 로그만 남기고 진행한다. Jira는 손대지 않은 상태로 남는다

**D. 해제는 다시 판정하지 않는다.** 스크립트가 `blocked` 카드를 처음 본 회차에 Jira 본문과 코멘트 수의 해시를 `triage_block_hash`로 기록하고, 이후 회차에 해시가 달라지면 `todo`로 되돌린다. 기획이 실제로 채워졌는지는 보지 않는다(그건 LLM 판단이고 이 스크립트는 판단하지 않는다). 워커가 멈춰서 `blocked`가 된 카드(`drain_state=stopped`)는 대상이 아니다.

## 알려진 틈

- 카드 생성과 첫 reconcile 회차 사이(최대 한 주기)에 본문이 바뀌면 그 변경은 기준 해시에 흡수돼 해제로 이어지지 않는다
- mirror 카드는 생성 직후 한 주기 동안 `todo`로 보인다
