# hook 설치 — 타임스탬프 수집

스킬은 ledger를 **읽기만** 한다. 쌓는 쪽은 hook이므로 한 번 설치해야 한다. 스킬 자체는 배포되지만 `~/.claude/hooks/`와 `settings.json`은 배포 대상이 아니다.

## 1. hook 스크립트 배치

```bash
cp ~/.claude/skills/nara-worklog/assets/nara-worklog-stamp.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/nara-worklog-stamp.py
```

심링크 대신 복사한다 — `~/.claude/hooks/*`는 실파일 규약이고, 스킬 디렉터리는 재설치 때 덮어써진다.

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
| ledger 디렉터리 자체가 없음 | settings.json 배선 누락, 또는 세션 재시작 안 함 |
| 디렉터리는 있는데 파일 없음 | 브랜치명에 `ABC-123` 형태 티켓 키가 없음 (의도된 skip) |
| 파일은 있는데 `list`가 비어 있음 | 미기록 시간이 1분 미만 (정상) |

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
