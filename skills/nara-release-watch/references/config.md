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
| `- owner/repo:some/dir` | **경로 감시** — 릴리즈 대신 그 경로를 건드린 커밋을 본다 |
| `- owner/repo @minor` | minor·major 변경만 |
| `- owner/repo @major` | major 변경만 |
| `# 제목`, `> 인용`, 산문 한 줄 | 무시 |
| `https://github.com/owner/repo/` | `owner/repo`로 정규화 |
| 같은 repo 중복 (대소문자 무관) | 첫 항목만 |
| 알 수 없는 마커 (`@nonsense`) | 기본값 `patch`로 폴백 — repo를 조용히 버리지 않는다 |

## 노이즈 필터 (전부 `watch.py`, LLM 0)

**highlights** — 릴리즈 본문의 PR 불릿에서 이런 것을 걷어내고 남은 줄이 watch 알림의 내용이 된다.

| 제거 대상 | 이유 |
|---|---|
| `fix`·`revert`·`chore`·`refactor`·`test`·`docs`·`build`·`ci`·`perf`·`style` prefix | stablyai/orca 실측: 주간 PR 불릿 617줄 중 8할 |
| `## Notable changes` 섹션 전체 | "Faster, smoother everyday use through..." 류의 마케팅 문장. 아래 PR 제목이 같은 정보를 더 잘 담는다 |
| "made their first contribution", "Full Changelog" | 보일러플레이트 |
| 후행 `by @user in <url>` | 항목 자체 URL은 남는다 |

경계는 단어 단위다 (`Fixture loader`는 `fix` 커밋이 아니다). 불릿이 없는 산문 본문은 highlights가 비고, 알림은 릴리즈 이름 + 링크로 폴백한다. 상한 30줄.

**첫 관측은 침묵** — 새 repo는 최신을 baseline으로 기록만 하고 아무것도 보고하지 않는다. 첫날 히스토리를 쏟으면 쓸모 있는 말을 하기 전에 무시당한다.

prerelease(alpha·beta·rc·dev·canary·next·nightly·preview·snapshot)는 **기본 제외**다. 태그 문자열로도 판정하므로 API 플래그를 안 붙이는 repo도 걸러진다. 판정은 구분자에 앵커되므로 `v1.0.0-aarch64`·`-source`·`-devtools` 같은 정식 태그는 걸리지 않는다.

### 경로 감시를 쓰는 경우

repo 릴리즈는 그 안의 특정 디렉터리가 바뀌었는지 알려주지 않는다. 실측 예: `mattpocock/skills`는 릴리즈가 2026-08-06에 멈췄는데 `skills/productivity/grill-me`는 2026-08-15에 바뀌었고 repo 전체는 계속 활발했다. 릴리즈로 감시하면 그 변경을 영구히 못 보고, repo 전체 커밋으로 감시하면 하루 여러 건이라 노이즈다.

- 릴리즈 모드와 **state가 분리**된다 (`repo` vs `repo:path`). 같은 repo를 repo 레벨 + 여러 경로로 동시에 감시해도 충돌하지 않는다
- watermark 단위가 태그 대신 **커밋 SHA**다. `@minor`/`@major`와 prerelease 필터는 SHA에 의미가 없어 실질적으로 무시된다 (16진수 SHA에는 prerelease 키워드가 나올 수 없다 — 모든 키워드가 비-16진수 문자를 하나 이상 포함한다)
- 경로에 커밋이 **0건**이면 `unwatchable`로 1회 보고된다. 거의 항상 경로 오타다
- `..`가 든 경로는 파싱 단계에서 버려진다

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

## 큐 — `~/.claude/release-watch-queue.json`

기계 소유. `poll`이 신규 항목(임계 통과분만)을 적재하고, digest가 판정·배달을 마친 뒤 `digest --drain`으로 비운다. `(repo, id)`로 dedup 하므로 state를 손으로 되감아 재폴링해도 중복 적재되지 않는다. 파일이 깨지면 백로그만 잃고 폴링은 계속된다.

```bash
python3 ~/.claude/skills/nara-release-watch/assets/watch.py digest           # 읽기만
python3 ~/.claude/skills/nara-release-watch/assets/watch.py digest --drain   # 배달 완료 후에만
```

## 설정

| 환경변수 | 기본값 | 비고 |
|---|---|---|
| `NARA_WATCHLIST` | `~/.claude/release-watch.md` | **절대경로** 권장 |
| `NARA_WATCH_STATE` | `~/.claude/release-watch-state.json` | **절대경로** 권장 |
| `NARA_WATCH_QUEUE` | `~/.claude/release-watch-queue.json` | **절대경로** 권장 |

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

**digest는 별도 autopilot으로 등록한다.** 같은 MCP 설정을 쓰되 에이전트를 분리한다 — watch 에이전트의 지시문이 "판정하지 말 것"이므로 한 에이전트에 두 단계를 겸하게 하면 그 계약이 흐려진다.

```
name:     Release-Digest
schedule: 주 1회, off-minute (예: 월 09:23 KST — `23 9 * * 1`)
prompt:   /nara-release-watch digest
```

큐는 드레인 전까지 쌓이므로 한 주를 걸러도 잃는 것이 없다. 사람이 중간에 직접 쳐도 되고, 그 경우 다음 주간 실행은 빈 큐를 보고 조용히 끝난다.

## 등록 — CronCreate (대안)

Multica를 안 쓸 때. CronCreate 잡은 **7일 후 자동 만료**되므로 self-renew가 필요하다. 일간 스케줄이라 만료 전에 7번은 발화하지만, 갱신하지 않으면 8일째 죽는다.

```
CronCreate(cron="47 8 * * *", prompt="/nara-release-watch", durable=true, recurring=true)
```

CronCreate는 dedup하지 않는다 — 호출마다 새 job ID를 만든다. 재등록할 때는 **반드시 `CronList` → `CronDelete` → `CronCreate`** 순서로. 단순 재생성은 중복 크론(하루 DM 2번)을 만든다. 상세 패턴은 `nara-trending-digest`의 Step 0 참조.
