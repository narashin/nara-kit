---
name: nara-slack-to-jira
description: >-
  Convert Slack thread permalinks into Jira tickets: classify Bug/Feature, dedup, draft → approve → create. English content.
  USE FOR: "slack to jira", "슬랙 티켓화", "스레드 티켓 만들어", Slack permalink + 티켓.
  DO NOT USE FOR: 버그 원인 분석 (→ /nara-incident), 요구사항 로컬화 (→ /nara-prep), AC 작성 (→ /nara-ac-draft).
---

# slack-to-jira — Slack 스레드 → Jira 티켓

슬랙 permalink N개 → 분류·중복검사 → draft 테이블 → 일괄 승인 → Jira create. 티켓 내용 영어. 리포터 구분 없음. 순차 처리.

참조: [Config](references/config.md) (profile 자동학습·라우팅), [Templates](references/templates.md) (영어 본문), [Dedup](references/dedup.md) (3분기·JQL·테이블)

## 파이프라인

1. **parse** — 링크 → `{channel_id, thread_ts}`. `p<TS>` 끝 6자리 앞 `.` → ts (`^\d{10}\.\d{6}$`)
2. **route** — channel_id → profile. 없으면 1회 학습 ([Config](references/config.md))
3. **fetch** — `get_thread_replies(channel_id, thread_ts)` 순차. timeout 시 최대 3회 재시도. 그래도 실패/접근 불가 → 행 error, 계속
4. **classify** — Bug | Feature. inline 힌트 override. 모호 → `[UNVERIFIED]`, 추측 금지
5. **dedup** — `jira_search` → known / related / new ([Dedup](references/dedup.md))
6. **draft** — 테이블 + 행별 펼침 영어 draft (1행이어도)
7. **approve** — 일괄 승인 / 수정·드롭 / class 변경 / new↔link
8. **execute** — new→`create_issue` (label = classification: `bug`|`feature` + profile `extra_labels`), related→+relates link, known→`add_comment`. 행별 실패 격리
9. **receipt** — output contract + side effects

## 규칙

- **승인 게이트 필수** — 일괄 승인 전 `jira_create_issue`/`add_comment`/`create_issue_link` 호출 금지. 단 사용자가 명시적으로 "draft 생략/바로 생성" 요청 시 그 요청이 곧 승인 → draft 건너뛰고 생성 (기본은 draft)
- 본문 영어 (`is_description_markdown=true`). 원문 verbatim 인용만 한국어 보존
- 스레드에 없는 값 창작 금지 → `_not specified_`. Feature AC: 충분→`[proposed]`, 부족→`_TBD_`
- priority/assignee/component 자동설정 안 함. profile은 스킬이 자동 성장
- label = classification (`bug`|`feature`) + profile `extra_labels`. `from-slack` 같은 출처 label 안 씀 ([Config](references/config.md) 라벨링)
- 멀티워크스페이스: 첫 fetch 실패 시 caveat (Slack MCP 팀 연결 확인)

## 출력

```
Slack→Jira batch done (applied).
- processed: N · created: n (Bug a/Feat b) KEYS · linked: m · dropped: k
- side effects: jira n created + m comments + p links · slack N read
- next: <검토 또는 후속>
```
