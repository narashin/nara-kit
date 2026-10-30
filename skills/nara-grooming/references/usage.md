# skills 사용량

skills 영역이 범위에 있고, 요청이 "안 쓰는 스킬", "스킬 정리", 사용량을 가리킬 때만 읽는다. 질문은 하나다. 이 스킬을 누가 실제로 불렀는가. 사실성(가리키는 경로가 아직 있나)은 [context-audit](context-audit.md)의 몫이다. 착안: autoharness의 사용률 기반 수명 관리(`tigerless-labs/autoharness@4f2a358`), 세션 기록 계수로 바꿔 가져왔다.

## 세기

```bash
CLAUDE_PROJECT_DIR=<툴킷 저장소> python3 scripts/usage.py
```

JSON 한 줄이 나온다. `window.days`는 세션 기록이 남아 있는 기간이다. 호스트가 오래된 기록을 지우므로 보통 한 달 남짓이다. 스크립트는 사용자 슬래시 호출, Skill 도구 호출, 그 스킬 폴더 밖 세션에서의 SKILL.md 읽기를 따로 센다. 스킬 소스 저장소 안에서 읽은 것은 개발이라 세지 않는다. 생성일은 `CLAUDE_PROJECT_DIR`의 `skills/<name>/` git 이력에서 얻는다.

| status | 뜻 | 처리 |
|---|---|---|
| `used` | 호출됨 | 보고 안 함 |
| `viewed` | 호출 없이 읽힘 | 보고 안 함. 읽힌 것은 쓰인 흔적이다 |
| `probation` | 이름이 창 안에서 생겼다 | 보고 안 함. 표본이 모자란다 |
| `unused` | 호출·읽기 0, 창보다 오래됨 | 아래 보정을 거친다 |
| `unverifiable` | 이력이 없어 나이를 모름 | 묶어서 센다 (외부 설치본이 대부분) |

## 보정: 이 기록에 안 보이는 실행

스크립트는 이 런타임의 세션 기록만 읽는다. `unused`마다 다음을 확인한 뒤에 처분 표에 올린다.

1. **스케줄러·배정 실행**: frontmatter에 `metadata.nara.scope: multica`가 있거나, 본문이나 README가 예약·autopilot·외부 도구 실행을 말하면 그 실행은 여기 안 남는다. `unverifiable (scheduler)`로 돌린다.
2. **다른 런타임**: 다른 런타임의 세션 디렉터리가 이 호스트에 있으면 두 형태로 찾는다. 사용자가 직접 부른 흔적(Codex는 `$<name>`)과, 모델이 스스로 골라 스킬 파일을 연 흔적(`skills/<name>/` 경로)이다. 예: `grep -rlE '\$<name>([^A-Za-z0-9_-]|$)|skills/<name>/' ~/.codex/sessions`. 하나라도 맞으면 그쪽에서 쓰인 것이니 후보에서 뺀다. 호출 형태만 찾으면 모델이 고른 사용이 빠진다. 2026-10 실측에서 한 스킬은 `$` 호출 1회에 파일을 연 세션이 16개였다. 맨 이름으로는 찾지 않는다. 세션마다 스킬 목록이 실려서 모든 이름이 걸린다. 세션 디렉터리를 읽을 수 없으면 `unused`가 아니라 `unverifiable (runtime)`이다.
3. **사용자가 이 대화에서 쓰는 중이라고 한 것**: 뺀다. 저장하지 않는다.

## 출력

보정을 통과한 `unused`만 `## Disposition`에 판정 `unused`로 올린다. 근거 칸에 창 길이와 보정 결과를 쓴다(예: `42일 호출 0 · 읽기 0 · Codex 호출·열람 0`). 처분 동작은 `archive`다. 툴킷 소스의 스킬(T3)에서 `archive`는 디렉터리를 소스에서 빼는 정확한 제안이고, git 이력이 보관 역할을 한다. 스킬 제거는 consumer에게 breaking이라는 것을 같이 적는다. 설치본은 `keep (vendor)`이거나 소스 경로 제안이다.

`unverifiable`은 행으로 펼치지 않는다. 같은 목록이 실행마다 반복되면 소음이 된다. receipt 한 줄에 이유별 수만 적는다.

receipt 숫자는 이렇게 센다.

- `unused <n>`: 보정을 통과해 처분 표에 올린 수.
- `unverifiable <m>`: 보정이 끝난 뒤의 수. 스크립트의 `age_unknown`에 보정에서 `scheduler`·`runtime`으로 돌린 것을 더한다. 스크립트의 `totals.unverifiable`과 다를 수 있다.
- `scope`의 `skills <N>`: 스크립트가 찾은 스킬 수. status와 무관하다. 이번 실행에서 보지 않은 영역은 0으로 적는다.
