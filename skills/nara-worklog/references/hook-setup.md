# hook 설치 — 타임스탬프 수집

스킬은 ledger를 **읽기만** 한다. 쌓는 쪽은 hook이므로 한 번 설치해야 한다. 스킬 자체는 배포되지만 `~/.claude/hooks/`와 `settings.json`은 배포 대상이 아니다.

## 1. hook 스크립트 배치

```bash
cp ~/.claude/skills/nara-worklog/assets/nara-worklog-stamp.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/nara-worklog-stamp.py
```

심링크 대신 복사한다 — `~/.claude/hooks/*`는 실파일 규약이고, 스킬 디렉터리는 재설치 때 덮어써진다.

**갱신**: 복사본이라 스킬 자산과 독립적으로 낡는다. `npx skills update` 뒤에는 위 `cp`를 다시 실행할 것. 정본은 `skills/nara-worklog/assets/nara-worklog-stamp.py`이고, 두 파일이 같은지는 `diff` 한 줄로 확인한다.

## 2. settings.json 배선

`~/.claude/settings.json`의 `hooks.UserPromptSubmit`과 `hooks.Stop` 배열에 **각각 새 그룹을 append**한다. 기존 그룹은 건드리지 않는다.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$HOME/.claude/hooks/nara-worklog-stamp.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$HOME/.claude/hooks/nara-worklog-stamp.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

`command` 타입만 쓴다. `prompt` 타입 hook은 매 턴 발동하면 모델이 지시로 오인한다.

## 3. 확인

티켓 브랜치가 있는 repo에서 한 턴 주고받은 뒤:

```bash
ls ~/.claude/worklog/                      # <TICKET>.jsonl 이 생겨야 함
python3 ~/.claude/skills/nara-worklog/assets/worklog.py list
```

비어 있으면 순서대로 확인:

| 증상 | 원인 |
|---|---|
| ledger 디렉터리 자체가 없음 | settings.json 배선 누락, 또는 세션 재시작 안 함. hook은 티켓 브랜치가 아니어도 배선만 되면 디렉터리를 만든다 |
| 디렉터리는 있는데 파일 없음 | 브랜치명에 `ABC-123` 형태 티켓 키가 없음 (의도된 skip). 팀 브랜치 규약이 소문자면(`feature/abc-123-x`) 정규식이 **영구히** 매칭하지 않는다 — 규약을 확인할 것 |
| 파일은 있는데 `list`가 비어 있음 | 미기록 시간이 1분 미만 (정상) |

**합격 기준은 "출력 없고 exit 0"이 아니다.** hook은 실패해도 조용히 종료하므로 고장 상태에서도 그 조건을 충족한다. 반드시 **ledger에 라인이 늘어났는지**로 판정할 것:

```bash
before=$(cat ~/.claude/worklog/<TICKET>.jsonl 2>/dev/null | wc -l)
# ... 한 턴 주고받기 ...
after=$(cat ~/.claude/worklog/<TICKET>.jsonl | wc -l)   # 늘어나야 정상
```

ledger 디렉터리가 쓰기 불가가 되거나 브랜치 규약이 어긋나면 수집이 조용히 멈추고, 몇 주 뒤 "올릴 시간이 없다"는 정상 응답만 받는다. 주기적으로 위 방식으로 확인할 것.

hook은 실패해도 조용히 종료한다 (턴을 막지 않는 것이 우선). 직접 검증하려면:

```bash
echo '{"hook_event_name":"UserPromptSubmit","session_id":"test","cwd":"'$PWD'"}' \
  | python3 ~/.claude/hooks/nara-worklog-stamp.py; echo "exit=$?"
```

출력이 없고 `exit=0`이면 정상이다 — `UserPromptSubmit` hook의 stdout은 모델 컨텍스트로 주입되므로 이 hook은 아무것도 출력하지 않아야 한다.

## 설정

| 환경변수 | 기본값 | 용도 |
|---|---|---|
| `NARA_WORKLOG_DIR` | `~/.claude/worklog` | ledger 위치 |
| `NARA_WORKLOG_GAP_MINUTES` | `30` | span을 자르는 idle 임계 |

## 제거

settings.json에서 두 그룹을 지우면 수집이 멈춘다. ledger는 남으므로 미기록 시간은 나중에도 올릴 수 있다.
