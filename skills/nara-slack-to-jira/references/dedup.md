# dedup — 후보 검색 + LLM 의미 판단 + 휴먼 게이트

목표: 스레드가 **기존 backlog 티켓에 이미 커버됐는지** 잡기 — 이 스킬이 안 만든, 표현·언어 제각각인 티켓이라도. JQL 키워드 매치는 **판정자가 아님** (LLM 요약이 매번 다르고 토큰 매치는 의역을 놓침). JQL은 후보만 모으고, **의미 판단은 LLM이 티켓을 읽고**, 최종 확정은 휴먼.

## 판정 순서

1. **임베디드 키** — 스레드에 `ABC-321` 인용 있으면 그대로 사용 (exact, 가장 확실)
2. **같은 스레드 재처리** — 티켓 Source에 박힌 Slack permalink로 exact 검색 (`description ~ "p<ts>"`) → summary 무관하게 결정적. 같은 스레드 두 번 던져도 잡음 (깔끔한 JQL 원하면 생성 시 `slack-thread-<ts>` label 추가 — 선택)
3. **backlog 겹침 (핵심 케이스)** — retrieve → 의미 판단:
   - a. 스레드에서 **검색어 여러 개** 생성 (기능 영역·컴포넌트·핵심 명사·동의어, 영어+원문 둘 다). recall 위해 넓게
   - b. `jira_search`로 후보 집합 수집 (open + 최근; 가능하면 component/label로). ~30-50개 cap, 관련도/최신순
   - c. LLM이 각 후보의 summary+description을 읽고 스레드와 **의미 비교** → known / related / new + 신뢰도 + 한 줄 근거. **토큰 매칭 아님**
   - d. 후보 + 근거를 draft에 노출 → 휴먼이 확정/번복

검색 JQL은 recall용 (정밀 아님):
```
project = <key> [AND <dedup_jql_base>] AND (summary ~ "<kw>" OR description ~ "<kw>")
```
- 여러 kw·언어를 OR로 넓게. `dedup_jql_base` 없으면 그 절 생략 (빈 `AND` 금지)

## known / related / new

| 상태 | 조건 (LLM 의미 판단) | 액션 |
|------|------|------|
| **known** | 의미상 동일 | 새로 안 만듦. 기존 티켓에 `jira_add_comment`(Slack 링크 + 새 맥락). 선택적 `duplicate` 링크 |
| **related** | 겹치지만 동일 아님 | `jira_create_issue` **+** `relates to` 링크(`jira_create_issue_link`) |
| **new** | 의미상 매치 없음 | `jira_create_issue`만 |

- 링크 타입명은 인스턴스마다 다름 → `jira_get_link_types`로 런타임 확인. 가정 금지
- 경계 케이스 → draft에 `possible duplicate: KEY` + 근거 노출. 휴먼 결정. **묵시적 병합 금지**

## 정직한 한계

- JQL = recall 전용, 정밀은 LLM, 최종은 휴먼
- **Jira에 의미검색(벡터) 없음** → 후보 recall은 키워드/컴포넌트/최근에 의존. 거대·비정형 backlog는 전부 못 읽음. draft에 **무엇을 검색했는지(JQL + 검사한 후보 N개)** 명시 → 커버리지 가시화. "결과 없음 = 확실히 신규" 침묵 금지
- recall이 후보를 못 가져오면 LLM도 못 봄 → 검색어를 넓게·여러 변형으로

## draft 테이블 (승인 게이트)

| # | link | →project | class | dedup | action | summary (EN) |
|---|------|----------|-------|-------|--------|--------------|
| 1 | p178… | ABC | Bug | new | CREATE Bug | "Login button unresponsive…" |
| 2 | p177… | ABC | Feature | known→ABC-123 | COMMENT ABC-123 | … |
| 3 | p179… | ABC | Feature | related→ABC-99 | CREATE + relates ABC-99 | … |

- 각 행은 펼치면 전체 영어 draft(title / description / AC / labels / links). dedup 행엔 LLM 근거 1줄 동반
- 1행이어도 테이블 거침
- 일괄 승인 시에만 execute. 승인 전 MCP 쓰기 호출 금지
- 행 단위 편집: approve all / edit row / drop row / change class / force new ↔ link
