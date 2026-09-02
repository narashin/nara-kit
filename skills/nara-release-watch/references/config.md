# watchlist 형식 · 씨딩 · 등록

## watchlist — `~/.claude/release-watch.md`

사람이 소유하는 마크다운이다. 설정 파일이 아니라 문서로 취급하므로 제목·산문·체크박스가 섞여도 된다.

```markdown
# release watchlist

> 취향대로 솎아낸 목록. 릴리즈 잦은 건 @minor 붙임.

## 에이전트 런타임
- anthropics/claude-code @minor    # 패치가 수백 건이라 minor 이상만
- openai/codex @minor

## 스킬 · 플러그인
- narashin/nara-kit
- obra/superpowers
- https://github.com/some/repo/    # URL 형태도 인식
```

파싱 규칙:

| 입력 | 결과 |
|---|---|
| `- owner/repo` | 모든 stable 릴리즈 알림 |
| `- owner/repo @minor` | minor·major 변경만 |
| `- owner/repo @major` | major 변경만 |
| `# 제목`, `> 인용`, 산문 한 줄 | 무시 |
| `https://github.com/owner/repo/` | `owner/repo`로 정규화 |
| 같은 repo 중복 (대소문자 무관) | 첫 항목만 |
| 알 수 없는 마커 (`@nonsense`) | 기본값 `patch`로 폴백 — repo를 조용히 버리지 않는다 |

prerelease(alpha·beta·rc·dev·canary·next·nightly·preview·snapshot)는 **기본 제외**다. 태그 문자열로도 판정하므로 API 플래그를 안 붙이는 repo도 걸러진다.

## 씨딩

```bash
python3 ~/.claude/skills/nara-release-watch/assets/watch.py seed --top 50
```

스타한 repo를 후보로 출력한다. **자동으로 watchlist에 넣지 않는다** — 스타는 다른 이유로도 누르니 노이즈다. 사람이 솎아서 붙인다.

## 상태 — `~/.claude/release-watch-state.json`

기계 소유. 매 실행 원자적으로 재작성된다 (`.tmp` → `os.replace`). 손으로 고칠 일은 두 가지뿐:

- **특정 repo를 다시 baseline** 하고 싶으면 그 항목의 `last_seen`을 지운다 → 다음 실행에서 최신을 baseline으로 잡고 침묵
- **놓친 릴리즈를 다시 잡으려면** `last_seen`을 과거 태그로 되돌린다

파일이 깨져도 폴링은 죽지 않는다 — 빈 상태로 읽고 전부 re-baseline 한다 (그날은 침묵).

## 설정

| 환경변수 | 기본값 | 비고 |
|---|---|---|
| `NARA_WATCHLIST` | `~/.claude/release-watch.md` | **절대경로** 권장 |
| `NARA_WATCH_STATE` | `~/.claude/release-watch-state.json` | **절대경로** 권장 |

상대경로도 동작하지만 실행 시 cwd 기준으로 해석되므로, cron·Multica처럼 cwd가 불확실한 환경에서는 다른 파일을 읽거나 쓰게 된다.

## 확인

```bash
python3 ~/.claude/skills/nara-release-watch/assets/watch.py list
python3 ~/.claude/skills/nara-release-watch/assets/watch.py poll --dry-run
```

`--dry-run`은 state를 쓰지 않으므로 반복 실행해도 baseline이 굳지 않는다.

## 등록 — Multica agent (권장)

`Trending-Digest`와 같은 자리다. 기존 autopilot이 Claude 풀을 절반쯤 쓰고 있으므로 **런타임은 Codex로** 붙인다 (키는 `custom_env`).

```
name:     Release-Watch
schedule: 매일 1회, off-minute (예: 08:47) — :00·:30은 전 세계가 몰리는 시각
prompt:   /nara-release-watch
```

조용한 날엔 이슈도 DM도 만들지 않는다. 즉 **매일 도는데 대개 아무 산출물이 없는 것이 정상**이다.

## 등록 — CronCreate (대안)

Multica를 안 쓸 때. CronCreate 잡은 **7일 후 자동 만료**되므로 self-renew가 필요하다. 일간 스케줄이라 만료 전에 7번은 발화하지만, 갱신하지 않으면 8일째 죽는다.

```
CronCreate(cron="47 8 * * *", prompt="/nara-release-watch", durable=true, recurring=true)
```

CronCreate는 dedup하지 않는다 — 호출마다 새 job ID를 만든다. 재등록할 때는 **반드시 `CronList` → `CronDelete` → `CronCreate`** 순서로. 단순 재생성은 중복 크론(하루 DM 2번)을 만든다. 상세 패턴은 `nara-trending-digest`의 Step 0 참조.
