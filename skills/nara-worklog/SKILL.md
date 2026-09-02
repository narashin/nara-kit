---
name: nara-worklog
description: >-
  Read the hook-collected session-timestamp ledger, propose per-day Jira worklog entries, then write them only after the user confirms.
  USE FOR: "worklog", "시간 기록해줘", "지라에 시간 올려", "작업 시간 올려줘", "안 올린 시간 있나", "/nara-worklog TICKET-ID".
  DO NOT USE FOR: 티켓 생성 (→ nara-slack-to-jira), 티켓 상태 전환 (→ jira MCP 직접), 큐 분류 (→ nara-jira-triage), 세션 회고 (→ nara-reflect).
---

# worklog — Jira Worklog from Session Timestamps

시간 산정은 결정론적 스크립트가 소유한다. 나는 표를 제시하고 승인만 받는다. **팀이 읽는 숫자이므로 승인 없이 쓰지 않는다.**

타임스탬프는 `nara-worklog-stamp.py` hook이 쌓는다. ledger 디렉터리(`~/.claude/worklog/`, `$NARA_WORKLOG_DIR`)가 없으면 hook 미설치 — [hook-setup.md](references/hook-setup.md) 안내 후 중단.

## Steps

1. **티켓 결정** — 인자 우선. 없으면 `git branch --show-current`에서 `[A-Z][A-Z0-9_]+-\d+` 추출. 둘 다 실패면 `worklog.py list` 결과를 보여주고 선택 요청.
2. **span 계산** — `python3 assets/worklog.py spans <TICKET>`. 이 JSON이 유일한 근거다. 내가 시각을 더하거나 빼지 않는다.
3. **승인 게이트 (생략 불가)** — 아래 Example 형태의 표를 제시하고 명시적 승인을 받는다.
   - 사람이 수정하면 수정값이 `time_spent`로 우선한다 (span 시각은 근거로 표에 남긴다).
   - `postable: false`인 날(1분 미만)은 표시만 하고 쓰지 않는다 — Jira가 0 worklog를 거부한다.
   - 일 합계가 8시간을 넘거나 이상하면 승인을 구하기 **전에** 그 사실을 지적한다.
4. **Jira 쓰기** — 승인된 날짜를 **오름차순**으로 `jira_add_worklog`, 날짜당 1건. `started`는 스크립트의 `jira_started` 값 그대로 쓴다(Jira는 밀리초 + 콜론 없는 offset을 요구). `comment`는 기본 생략, `original_estimate`·`remaining_estimate`는 사람이 명시하지 않으면 건드리지 않는다.
5. **watermark 기록** — `python3 assets/worklog.py record <TICKET> --through <ISO> --seconds <N> --worklog-id <ID>`
   - 전부 성공 → `--through`는 `spans` 출력의 `latest_event`.
   - 중간 실패 → 성공한 **마지막 날짜의 마지막 span end**. 실패한 날은 다음 실행에 다시 제안된다.
   - 쓰기 0건이면 record 금지. `jira_add_worklog`는 멱등이 아니라서 이 watermark가 유일한 중복 방지 장치다.
6. **receipt** — Outcome / Evidence(날짜별 시간 + worklog id) / Artifact(ledger 경로) / Next Action.

## Example

ledger `~/.claude/worklog/PROJ-431.jsonl` →

```
09:12 prompt    ┐
09:20 turn_end  │ 53m   ← 09:48 prompt까지 28m 공백은 출력 읽는 시간, 작업으로 계산
09:48 prompt    │
10:05 turn_end  ┘
   ── 2h51m 자리 비움 → 분할, 청구 안 함 ──
12:56 prompt    ┐ 34m
13:30 turn_end  ┘
```

승인 요청 표:

| 날짜 | span | 길이 | 일 합계 |
|---|---|---|---|
| 2026-09-02 | 09:12–10:05 / 12:56–13:30 | 53m / 34m | **1h 27m** |

승인 시 `jira_add_worklog(issue_key="PROJ-431", time_spent="1h 27m", started="2026-09-02T09:12:00.000+0900")`.

## Time Model

- `prompt → turn_end`는 길어도 **자르지 않는다** — 에이전트 실행은 작업 시간이다.
- 나머지 구간만 idle 임계(기본 30분, `--gap-minutes` / `$NARA_WORKLOG_GAP_MINUTES`)로 자른다: `turn_end → prompt`는 자리 비움, `turn_end` 없는 `prompt → prompt`는 턴 중간에 죽은 세션.
- 자정 분할 → 날짜별 집계. 한 티켓의 워크트리 여러 개는 한 ledger에 모여 **합집합**으로 병합된다(세션별 합산이면 중복 계상). 분 단위 내림.

## Error Handling

- ledger 디렉터리 없음 → hook 미설치. hook-setup.md 안내 후 중단.
- 해당 티켓 ledger 없음 → 그 브랜치 작업 기록이 없다는 뜻. 티켓 오타 확인 요청.
- 미기록 span 0건 → `이미 전부 기록됨` receipt로 종료. Jira 호출 금지.
- Jira MCP 미연결 → 표만 출력하고 수동 입력으로 넘긴다 (`recorded only`).
- worklog 권한 오류 → 사람에게 권한 확인 요청. watermark 기록 금지.
