---
name: nara-release-watch
description: >-
  First poll a watchlist of GitHub repos for new releases, then judge each against the nara-kit surface and report only what is worth distilling.
  USE FOR: "release watch", "watchlist 확인", "새 릴리즈", "증류할 거 있나", "릴리즈 감시".
  DO NOT USE FOR: 모르는 repo 발견 (→ nara-trending-digest), 라이브러리 문서 (→ Context7), 스킬 개선 (→ nara-skill-forge).
---

# release-watch — Watchlist 릴리즈 증류 판정

두 층으로 나뉜다. **신규 릴리즈가 0건이면 LLM을 깨우지 않는다** — 조용한 날의 비용은 repo당 API 한 방이다.

```
watchlist (사람 관리)  ~/.claude/release-watch.md
      ↓  assets/watch.py poll · LLM 0
신규 릴리즈 diff  ──→ quiet && !needs_attention 이면 여기서 종료, 무알림
      ↓  있을 때만
증류 판정 → Slack DM + Obsidian
```

## Steps

1. **폴링** — `python3 assets/watch.py poll --limit 5`. 출력 JSON이 유일한 입력이다.
2. **조기 종료 판정** — `quiet: true`이고 `needs_attention: false`면 **아무것도 보내지 않고** 종료한다. 조용한 날에 "없음"을 보내면 6일치 무소식이 7일째 진짜 소식을 덮는다. receipt만 남긴다.
3. **판정** — `new[]` 각 항목을 [distill-rubric.md](references/distill-rubric.md) 4분류로 판정한다. `의존`이 기본값이다. 판정 근거로 nara-kit 스킬 표면을 확인하되, 겹친다고 주장할 때는 **그 스킬 이름을 명시**한다 — 이름을 못 대면 `이미 있음`이 아니다.
4. **배달** — `nara-trending-digest`와 같은 경로. `mcp__slack__get_me` → `post_message`(DM), 그리고 Obsidian `Inbox/release-watch-<YYYY-MM-DD>.md`. `--dry-run`이면 터미널 출력만.
5. **needs_attention 처리** — `failed[]`(인증·rate·404)는 매 실행 보고한다. `unwatchable[]`(릴리즈·태그 둘 다 없음)은 최초 1회만 보고되고 이후 억제된다 — watchlist에서 빼거나 그대로 둘지는 사람 판단.
6. **receipt** — Outcome / Evidence(checked·new·suppressed 수) / Artifact(Obsidian 경로) / Next Action.

## Example

```
$ python3 assets/watch.py poll --limit 5
{ "checked": 12, "suppressed": 3, "new": [
    { "repo": "obra/superpowers", "id": "v3.0.0", "url": "...", "body": "..." } ],
  "baselined": [], "unwatchable": [], "failed": [], "quiet": false, "needs_attention": false }
```

→ 판정 1건만 돌리고 DM 발송. `suppressed: 3`은 `@minor` 임계에 걸린 패치 릴리즈이므로 판정하지 않는다.

`checked: 12, new: [], quiet: true, needs_attention: false` → **Step 2에서 종료.** LLM 판정도, DM도 없다.

## Watch Modes

| watchlist 표기 | 감시 대상 | watermark |
|---|---|---|
| `owner/repo` | releases → 없으면 tags | 태그 |
| `owner/repo:some/dir` | 그 경로를 건드린 커밋 | 커밋 SHA |

경로 모드는 repo 릴리즈가 특정 디렉터리의 변경을 대변하지 못할 때 쓴다 — 릴리즈가 멈췄거나, repo 전체 커밋이 너무 잦아 노이즈일 때. state는 `repo:path`로 분리 기록되므로 같은 repo를 repo 레벨과 여러 경로로 동시에 감시할 수 있다. 판정 루브릭은 두 모드에 동일하게 적용된다.

## Noise Control

- **prerelease 기본 제외** — API 플래그와 태그 문자열 둘 다 본다. `openai/codex`는 `rust-v0.153.0-alpha.5`를 플래그 없는 정식 릴리즈로 올린다. `--include-prerelease`로 해제.
- **`@minor` / `@major` 임계** — watchlist 항목 뒤에 붙인다. `anthropics/claude-code`는 패치 릴리즈가 수백 건이라 임계 없이 두면 매일 발화한다. 억제된 릴리즈도 `last_seen`은 전진하므로 같은 릴리즈를 매번 재평가하지 않는다.
- **첫 관측은 침묵** — 새 repo는 현재 최신을 baseline으로 기록하고 아무것도 보고하지 않는다. 첫날 히스토리를 쏟으면 쓸모 있는 말을 하기 전에 무시당한다.
- 버전을 파싱할 수 없으면 **억제하지 않는다** — 못 읽는 걸 숨기는 게 더 나쁘다.

## Config

| 파일 | 소유 | 내용 |
|---|---|---|
| `~/.claude/release-watch.md` | 사람 | watchlist. `owner/repo [@minor\|@major]`, 마크다운 산문 허용 |
| `~/.claude/release-watch-state.json` | 기계 | repo별 `last_seen`. 매 실행 원자적 재작성 |

두 파일을 분리한 이유: 상태가 매번 덮어쓰이므로 사람이 편집 중인 목록과 같은 파일에 둘 수 없다. 형식·씨딩·등록 절차는 [config.md](references/config.md).

## Error Handling

- watchlist 없음·빈 목록 → `empty_watchlist` 반환. `assets/watch.py seed`로 스타에서 후보를 뽑아 제시하고 사람이 솎아내게 한다. 내가 목록을 만들지 않는다.
- `gh` 미인증 → `failed[]`에 전부 담긴다. `gh auth login --hostname github.com` 안내. **state를 건드리지 않으므로** 복구 후 놓친 릴리즈가 그대로 잡힌다.
- Slack 실패 → Obsidian 저장은 계속하고 `→ ESCALATE: Slack 전송 실패`.
- Obsidian 실패 → 터미널 출력 fallback.
