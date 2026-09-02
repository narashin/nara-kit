# nara-worklog — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

세션 타임스탬프 ledger를 날짜별 Jira worklog로 올린다. 사람 승인 게이트가 있다.

## 호출

- Claude Code: `/nara-worklog` 또는 `/nara-worklog PROJ-431`
- Codex: `$nara-worklog`
- 직접 실행: `python3 skills/nara-worklog/assets/worklog.py spans PROJ-431`
- 미기록 시간 훑기: `python3 skills/nara-worklog/assets/worklog.py list`

**hook을 먼저 설치해야 한다** — [references/hook-setup.md](references/hook-setup.md). 스킬은 ledger를 읽기만 하고, 쌓는 쪽은 hook이다.

## 언제 쓰나

- **USE FOR:** "worklog", "시간 기록해줘", "지라에 시간 올려", "작업 시간 올려줘", "안 올린 시간 있나".
- **DO NOT USE FOR:** 티켓 생성 (→ nara-slack-to-jira), 티켓 상태 전환 (→ jira MCP 직접), 큐 분류 (→ nara-jira-triage), 세션 회고 (→ nara-reflect).

## 왜 이렇게 쪼갰나

시작 시각은 "기록해야 한다는 걸 알기 전"에 이미 지나가 있다. LLM에게 "세션 시작할 때 스탬프를 찍어라"라고 선언해도 안 지켜지는 종류의 의무다. 그래서 **수집은 hook**(결정론적, 잊을 수 없음, 토큰 0).

반대로 Jira 쓰기를 hook에 두면 안 된다. hook은 shell이라 MCP를 못 쓰고, 무엇보다 **팀이 읽는 티켓에 확인 없이 숫자가 올라간다**. 세션 wall-clock은 점심·회의·안 닫은 터미널을 다 포함하므로 그대로 올리면 과대계상이다. 그래서 **쓰기는 스킬**(집계 + 사람 승인).

## 시간을 어떻게 세나

`prompt`·`turn_end` 이벤트로 상호작용 구간을 만든다.

```
09:12 prompt     ┐
09:20 turn_end   │  53m
09:48 prompt     │   ← 28m 출력 읽는 시간, 작업으로 계산
10:05 turn_end   ┘
   ── 2h51m 자리 비움 → 분할, 청구 안 함 ──
12:56 prompt     ┐  34m
13:30 turn_end   ┘
                 합계 1h 27m
```

- `prompt → turn_end` 구간은 길어도 안 자른다 — 에이전트가 도는 시간은 작업 시간이다.
- 그 외 구간이 **90분**(`--gap-minutes`) 넘으면 자른다. 30분은 기획 검수 같은 1시간 안쪽 유휴를 잘라내서 상향했다.
- 자정 분할 → 날짜별 1건. 여러 날 걸린 티켓이 PR 날짜에 뭉치지 않는다.
- 한 티켓 워크트리 2개는 **합집합**으로 병합 (세션별 합산이면 중복 계상).
- 분 단위 **내림**. 안 쓴 1분을 청구하지 않는다.

## subtask 귀속

브랜치 하나로 여러 subtask를 오갈 때는 전환 마커를 찍는다.

```
python3 skills/nara-worklog/assets/worklog.py mark PROJ-500
```

마커 이후 구간이 그 티켓 소유가 되고, 출력이 `(날짜 × 티켓)` 버킷으로 나뉘어 Jira 쓰기도 버킷당 1건이 된다. 마커는 시간을 만들거나 없애지 않는다 — span을 자를 뿐이다.

**마커 없이 지난 시간은 사후에 나눌 수 없다.** hook은 브랜치명의 티켓 키만 알기 때문이다.

## 중복 방지

`jira_add_worklog`는 멱등이 아니다. 그래서 Jira 쓰기가 성공한 뒤 ledger에 `logged` watermark를 append하고, 다음 실행은 그 이후 구간만 제안한다. 중간에 실패하면 그 지점에서 멈추고 직전까지만 watermark를 올린다. 하루 안에서 귀속이 교차하면 단일 커서로는 구멍을 표현할 수 없어 한계가 있다 — `docs/review/` 참조.

## 설계 메모

시간 산정은 `assets/worklog.py`(표준 라이브러리만)가 소유한다. LLM이 시각을 더하면 같은 ledger에서 매번 다른 숫자가 나오고, 그 숫자는 팀 스프린트 리포트에 들어간다. 테스트는 `assets/test_worklog.py` — `python3 -m pytest skills/nara-worklog/assets/test_worklog.py -q`.

hook 스크립트 정본은 `assets/nara-worklog-stamp.py`이고, `~/.claude/hooks/`에는 복사본을 둔다 (심링크 아님 — 스킬 재설치 때 덮어써진다).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
- hook 설치: [references/hook-setup.md](references/hook-setup.md)
