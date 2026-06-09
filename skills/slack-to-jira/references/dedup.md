# dedup — 3분기 판정·JQL·draft 테이블

스레드마다 기존 Jira 티켓과 대조해 `known` / `related` / `new` 중 하나로 판정한다.

## 키워드 추출 → JQL

1. 스레드에서 키워드 추출 (기능 영역·에러 시그니처·컴포넌트)
2. `jira_search` 호출:
   ```
   project = <key> AND <dedup_jql_base> AND (summary ~ "<kw>" OR description ~ "<kw>")
   ```
3. 스레드에 Jira 키/링크(`ABC-321` 형태)가 이미 있으면 직접 포착 — 검색보다 우선

## 3분기 판정

| 상태 | 조건 | 액션 |
|------|------|------|
| **known** | 고신뢰 완전 중복 | 새로 안 만듦. 기존 티켓에 `jira_add_comment`(Slack 링크 + 새 맥락). 선택적으로 `duplicate` 링크 |
| **related** | 겹치지만 동일은 아님 | 새로 `jira_create_issue` **+** `relates to` 링크(`jira_create_issue_link`) |
| **new** | 매치 없음 | `jira_create_issue`만 |

- 링크 타입명("Relates"/"Duplicate")은 인스턴스마다 다름 → 런타임에 `jira_get_link_types`로 확인. 가정 금지
- 경계 케이스(저신뢰 매치) → draft에 `possible duplicate: KEY` 노출. 사용자가 merge/new 결정. **묵시적 병합 금지**

## draft 테이블 (승인 게이트)

| # | link | →project | class | dedup | action | summary (EN) |
|---|------|----------|-------|-------|--------|--------------|
| 1 | p178… | ABC | Bug | new | CREATE Bug | "Login button unresponsive…" |
| 2 | p177… | ABC | Feature | known→ABC-123 | COMMENT ABC-123 | … |
| 3 | p179… | ABC | Feature | related→ABC-99 | CREATE + relates ABC-99 | … |

- 각 행은 펼치면 전체 영어 draft(title / description / AC / labels / links)
- 1행이어도 테이블 거침
- 일괄 승인 시에만 execute. 승인 전 MCP 쓰기 호출 금지
- 행 단위 편집: approve all / edit row / drop row / change class / force new ↔ link
