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
            "command": "for P in /opt/homebrew/bin/python3 /usr/bin/python3; do [ -x \"$P\" ] && exec \"$P\" \"$HOME/.claude/hooks/nara-worklog-stamp.py\"; done; exit 0",
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
            "command": "for P in /opt/homebrew/bin/python3 /usr/bin/python3; do [ -x \"$P\" ] && exec \"$P\" \"$HOME/.claude/hooks/nara-worklog-stamp.py\"; done; exit 0",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

`command` 타입만 쓴다. `prompt` 타입 hook은 매 턴 발동하면 모델이 지시로 오인한다.

### 인터프리터를 절대경로로 쓰는 이유

**`python3`를 그냥 쓰면 안 된다.** PATH가 pyenv shim으로 해석되면 shim이 버전 해석을 위해 프로세스를 더 포크하고, 그게 순수 오버헤드가 된다 — 실측 **438.8ms vs 55.1ms**(8배). 이 hook은 턴당 2회 발동하므로 턴당 약 0.77초가 그냥 사라진다. 스크립트 자체 비용은 그중 40ms뿐이다.

경로를 하나만 박지 않고 체인으로 두는 이유:

- **버전을 고정하지 않는다** — `~/.pyenv/versions/3.12.8/bin/python3`이 제일 빠르지만(18.8ms) pyenv 업그레이드로 그 경로가 사라지면 exec가 실패해 **모든 턴이 막힌다**
- **`exec`가 종료 코드를 보존한다** — hook이 exit 2로 차단해야 하는 경우(예: PreToolUse 게이트)가 그대로 동작한다 (실측 확인)
- **`; exit 0`이 fail-open을 보장한다** — 두 경로가 다 없으면 마지막 `[ -x ]` 실패가 exit 1이 되므로, 명시적으로 0을 반환해 bookkeeping 부재가 턴을 막지 않게 한다

두 hook 모두 3.9에서 컴파일되므로 `/usr/bin/python3` 폴백이 실제로 유효하다. 이 파일들을 수정할 때 3.10+ 문법(`X | Y` 애노테이션 등)을 쓰면 폴백이 깨진다.

**실제로 깨뜨린 적이 있다.** `-> str | None`을 추가했더니 3.9에서 `TypeError`로 `exit=1`이 났다. 폴백이 발동하는 머신에서는 그게 곧 모든 턴 차단이다. 첫 줄의 `from __future__ import annotations`가 이 방어이므로 지우지 말 것. 확인은 한 줄이다:

```bash
echo '{"hook_event_name":"Stop","cwd":"/"}' | /usr/bin/python3 ~/.claude/hooks/nara-worklog-stamp.py; echo $?
```

`0`이 아니면 폴백이 깨진 상태다.

## 2b. Codex 배선

Codex도 `UserPromptSubmit`과 `Stop`을 같은 이름으로 노출하므로 같은 스크립트를 쓴다. 배선은 `~/.codex/hooks.json`의 해당 배열에 그룹을 append한다.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "for P in /opt/homebrew/bin/python3 /usr/bin/python3; do [ -x \"$P\" ] && exec \"$P\" \"$HOME/.claude/hooks/nara-worklog-stamp.py\" --event prompt; done; exit 0",
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
            "command": "for P in /opt/homebrew/bin/python3 /usr/bin/python3; do [ -x \"$P\" ] && exec \"$P\" \"$HOME/.claude/hooks/nara-worklog-stamp.py\" --event turn_end; done; exit 0",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**`--event`를 명시로 넘긴다.** 페이로드의 `hook_event_name`으로도 동작하지만, 그러면 두 harness의 페이로드 스키마가 계속 같다는 데 시계가 걸린다. 인자로 넘기면 페이로드가 비어도 찍힌다.

**손으로 편집하지 말 것.** 실제로 두 번 틀렸다 — `UserPromptSubmit` 대신 `PostToolUse`에 넣었고(도구 호출마다 발동해 턴 경계가 무의미해진다), 닫는 괄호를 빠뜨려 파일 전체가 파싱 불가가 됐다. 후자는 worklog만 죽는 게 아니라 **그 파일의 모든 hook**(orca·paseo 등)이 함께 죽는다. 아래처럼 파서를 거쳐 append한다.

```bash
python3 - <<'PY'
import json
path = f"{__import__('os').path.expanduser('~')}/.codex/hooks.json"
data = json.load(open(path, encoding="utf-8"))
for event, name in (("UserPromptSubmit", "prompt"), ("Stop", "turn_end")):
    arr = data["hooks"].setdefault(event, [])
    if any("worklog" in h.get("command", "") for g in arr for h in g.get("hooks", [])):
        continue
    cmd = ('for P in /opt/homebrew/bin/python3 /usr/bin/python3; do '
           '[ -x "$P" ] && exec "$P" "$HOME/.claude/hooks/nara-worklog-stamp.py" '
           f'--event {name}; done; exit 0')
    # A new group, not an existing one: the other groups carry matchers and
    # belong to other tools, so sharing one lets an unrelated edit drop this.
    arr.append({"hooks": [{"type": "command", "command": cmd, "timeout": 10}]})
with open(path, "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print("wired")
PY
```

**⚠️ 이 배선 직후 hook 신뢰 모달이 다시 뜬다.** 앞서 "Trust all"을 눌러둔 상태에서도 `hooks.json`이 바뀌면 "Hooks need review — N hooks are new or changed"가 다시 뜬다(실측). 그리고 **그 모달은 초기 프롬프트를 삼킨다** — `codex "..."`로 넘긴 지시가 사라지고 빈 컴포저에 앉는다. `orca`는 모달이 열린 agent 터미널로의 입력 주입을 `agent_prompt_blocked`로 거부하므로 자동 응답도 불가능하다.

따라서 배선 직후 **사람이 인터랙티브 세션에서 한 번 눌러야 한다**(`2` Trust all). 그 전까지 무인 워커 세션(`multica-dispatch.py`)은 전부 그 모달에서 멈춘다. 신뢰는 전역 저장이라 한 번으로 끝난다.

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

### 별개 검사: 침묵 계약

아래는 "수집이 되는지"가 아니라 **"hook이 턴을 오염시키지 않는지"**를 확인하는 것이다. 두 검사를 섞지 말 것 — 이건 고장 상태에서도 통과한다.

```bash
echo '{"hook_event_name":"UserPromptSubmit","session_id":"test","cwd":"'$PWD'"}' \
  | python3 ~/.claude/hooks/nara-worklog-stamp.py; echo "exit=$?"
```

출력이 없고 `exit=0`이어야 한다 — `UserPromptSubmit` hook의 stdout은 모델 컨텍스트로 주입되고 non-zero exit은 턴을 막는다. 수집이 되는지는 위의 ledger 라인 수로만 판정한다.

## 설정

| 환경변수 | 기본값 | 용도 |
|---|---|---|
| `NARA_WORKLOG_DIR` | `~/.claude/worklog` | ledger 위치 |
| `NARA_WORKLOG_GAP_MINUTES` | `90` | span을 자르는 idle 임계. 1 이상의 정수 |

## 제거

settings.json에서 두 그룹을 지우면 수집이 멈춘다. ledger는 남으므로 미기록 시간은 나중에도 올릴 수 있다.
