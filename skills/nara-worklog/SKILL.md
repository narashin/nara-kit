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
3. **승인 게이트 (생략 불가)** — 아래 Example 형태의 표를 제시하고 명시적 승인을 받는다. 단위는 **(날짜 × 티켓)** 버킷이다.
   - 사람이 수정하면 수정값이 `time_spent`로 우선한다 (span 시각은 근거로 표에 남긴다).
   - `postable: false`인 버킷(1분 미만)은 표시만 하고 쓰지 않는다 — Jira가 0 worklog를 거부한다. 목록은 `unpostable`.
   - 일 합계가 8시간을 넘거나 이상하면 승인을 구하기 **전에** 그 사실을 지적한다. Jira가 8시간을 `1d`로 렌더링하는 인스턴스에서는 승인한 `9h 34m`이 `1d 1h 34m`으로 보인다 — 저장된 초는 정확하니 사람이 오기로 오인해 지우지 않도록 함께 알린다.
   - **부모 티켓에 귀속된 버킷이 있으면 지적한다.** subtask가 있는 티켓인데 마커 없이 부모로 잡힌 구간은 대개 `mark`를 잊은 것이다 (Step 4 참조). `jira_get_issue`로 subtask 유무를 확인해 알린다.
   - 쓰기 **전에** `jira_get_worklog`로 각 대상 티켓의 기존 worklog를 확인해 같은 날 중복이 없는지 대조한다. watermark는 이 ledger 안에서만 유효하고, 다른 경로로 이미 올라간 기록은 모른다.
4. **Jira 쓰기** — 승인된 버킷을 **시각 오름차순**으로 `jira_add_worklog`, 버킷당 1건. `issue_key`는 버킷의 `ticket`(마커가 있으면 subtask), `started`는 그 버킷의 `jira_started` 값 그대로(Jira는 밀리초 + 콜론 없는 offset을 요구). `comment`는 기본 생략, `original_estimate`·`remaining_estimate`는 사람이 명시하지 않으면 건드리지 않는다.
5. **watermark 기록** — `python3 assets/worklog.py record <TICKET> --through <ISO> --seconds <N> --worklog-id <ID>`
   - `--through`는 **offset을 포함한** ISO여야 한다(`2026-09-02T10:05:00+09:00`). offset 없는 값은 거부된다 — ledger는 append-only라 되돌릴 수 없고, naive watermark 하나가 이 티켓의 `spans`와 (디렉터리 전체를 훑는) `list`를 영구히 깨뜨린다. **`spans` 출력의 값을 그대로 복사해 쓴다.**
   - 전부 성공 → `--through`는 `spans` 출력의 `latest_event`.
   - 중간 실패 → 성공한 **마지막 날짜의 마지막 span end**. 그 뒤의 날은 다시 제안되지만, **건너뛴 중간 날은 다시 제안되지 않는다** — watermark가 단일 커서라 구멍을 표현할 수 없다. 오름차순으로 쓰다가 실패하면 **거기서 멈추고** 그 직전까지만 기록할 것.
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

승인 요청 표 — **행은 버킷 단위이고 티켓 열이 필수다.** 하루를 한 행으로 접으면 티켓별 분배가 승인에서 숨는다.

| 날짜 | 티켓 | span | 버킷 합계 |
|---|---|---|---|
| 2026-09-02 | PROJ-431 | 09:12–10:05 / 12:56–13:30 | **1h 27m** |
| | | 일 합계 | **1h 27m** |

승인 시 `jira_add_worklog(issue_key="PROJ-431", time_spent="1h 27m", started="2026-09-02T09:12:00.000+0900")` 1건.

마커가 있으면 같은 하루가 여러 행이 되고 **쓰기도 행마다 1건**이다:

| 날짜 | 티켓 | span | 버킷 합계 |
|---|---|---|---|
| 2026-09-02 | PROJ-431 | 09:12–09:20 | **8m** |
| 2026-09-02 | PROJ-500 | 09:20–10:05 / 12:56–13:30 | **1h 19m** |
| | | 일 합계 | **1h 27m** |

→ `jira_add_worklog` 2건 (`PROJ-431` 8m, `PROJ-500` 1h 19m). 두 번째 버킷의 `started`는 **09:20**(그 버킷의 첫 span)이다.

## Subtask Attribution

브랜치 하나로 여러 subtask를 오갈 때 쓴다. hook은 브랜치명에서 티켓 키만 뽑으므로, 마커 없이는 어느 구간이 어느 subtask였는지 **복구 불가능하다** — 추측해서 채우지 말 것.

```
python3 assets/worklog.py mark ASOPS-121     # 지금부터 이 subtask
```

- 마커는 **브랜치 티켓의 ledger**에 append된다 (hook이 쓰는 그 파일). subtask별 ledger가 새로 생기지 않는다.
- 마커 이후 구간은 다음 마커까지 그 티켓 소유다. 첫 마커 **이전** 구간은 브랜치 티켓(=대개 부모)에 남는다.
- 마커는 시간을 만들거나 없애지 않는다 — span을 자를 뿐이라 귀속 합계는 항상 원본 합계와 같다.
- 유휴 구간에 찍힌 마커는 자기 시간을 갖지 않고 다음 span의 소유자만 정한다.
- 사용자가 "이제 E3 한다" 류로 작업 대상을 밝히면 **`mark`를 제안한다.** 사후에 정확히 나눌 방법은 없다.

## Time Model

- `prompt → turn_end`는 길어도 **자르지 않는다** — 에이전트 실행은 작업 시간이다.
- 나머지 구간만 idle 임계(**기본 90분**, `--gap-minutes` / `$NARA_WORKLOG_GAP_MINUTES`)로 자른다: `turn_end → prompt`는 자리 비움, `turn_end` 없는 `prompt → prompt`는 턴 중간에 죽은 세션.
- 임계가 90분인 이유: 실측 하루에서 30분은 62분짜리 기획 검수 유휴와 55분 유휴를 청구에서 잘라냈고, 90분은 그것을 살리면서 707분(수면) 유휴는 그대로 버린다. 생각·검수 시간은 작업 시간이라는 판단이다.
- 자정 분할 → 날짜별 집계. 한 티켓의 워크트리 여러 개는 한 ledger에 모여 **합집합**으로 병합된다(세션별 합산이면 중복 계상). 분 단위 내림.

## Error Handling

- ledger 디렉터리 없음 → hook 미설치. hook-setup.md 안내 후 중단.
- 해당 티켓 ledger 없음 → 그 브랜치 작업 기록이 없다는 뜻. 티켓 오타 확인 요청.
- 미기록 span 0건 → `이미 전부 기록됨` receipt로 종료. Jira 호출 금지.
- Jira MCP 미연결 → 표만 출력하고 수동 입력으로 넘긴다 (`recorded only`).
- worklog 권한 오류 → 사람에게 권한 확인 요청. watermark 기록 금지.
