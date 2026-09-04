---
name: nara-release-watch
description: >-
  Poll a watchlist of GitHub repos, report what shipped without judging it, and queue each item; then judge the accumulated queue weekly for what is worth distilling.
  USE FOR: "release watch", "watchlist 확인", "새 릴리즈", "릴리즈 감시", "release digest", "증류할 거 있나".
  DO NOT USE FOR: 모르는 repo 발견 (→ nara-trending-digest), 라이브러리 문서 (→ Context7), 스킬 개선 (→ nara-skill-forge).
---

# release-watch — 알림(watch)과 증류 판정(digest)의 2단계

판정을 릴리즈 단위로 매일 하면 릴리즈 잦은 repo는 감시가 불가능하다 — 임계를 붙이면 알림까지 죽고, 안 붙이면 매일 발화한다 (stablyai/orca: minor 고정 + 일간 패치). 그래서 알림은 매일 기계 필터로, 판정은 주 1회 큐 누적분을 놓고 한다.

```
watchlist → poll (LLM 0) → quiet면 종료, 무알림
              ↓ 있을 때만
         [watch] 알림(판정 없음) → DM + Obsidian, 큐 적재
              ⋮
         [digest · 주 1회] 큐 전체 판정 → 배달 → 드레인
```

## Mode: watch (기본 — `/nara-release-watch`, autopilot이 도는 단계)

1. **폴링** — `python3 assets/watch.py poll --limit 5`. 출력 JSON이 유일한 입력이고 신규 항목은 큐에도 적재된다(`queued`). 출력의 `"judgment": "forbidden"`이 이 실행의 계약이다.
2. **조기 종료** — `quiet: true`이고 `needs_attention: false`면 **아무것도 보내지 않고** 종료한다. 조용한 날의 "없음"은 진짜 소식이 있는 날을 덮는다. receipt만 남긴다.
3. **알림 작성** — `new[]` 각 항목을 **판정 없이** 전달: repo · 버전 · 링크 · `highlights[]`(기계 필터 통과분). highlights가 비면 이름 + 링크만. 증류 판정·"우리도 만들자" 제안 금지 — 그건 digest의 일이다.
4. **배달** — `mcp__slack__get_me` → `post_message`(DM) + Obsidian `Inbox/release-watch-<YYYY-MM-DD>.md`. `--dry-run`이면 터미널만.
5. **needs_attention** — `failed[]`(인증·rate·404)는 매 실행 보고. `unwatchable[]`은 최초 1회만 — 빼거나 둘지는 사람 판단.
6. **receipt** — 첫 줄에 `stage: watch (판정 없음)` **필수**. 이어서 Outcome / Evidence(checked·new·suppressed·queued) / Artifact / Next Action(큐 N건 — `/nara-release-watch digest`). 이 줄 위에 판정이 있으면 단계를 벗어난 것이다. 판정을 지운다.

## Mode: digest (주간 — `/nara-release-watch digest`)

1. **큐 읽기** — `python3 assets/watch.py digest`. `count: 0`이면 "빈 큐" 보고 후 종료.
2. **판정** — 큐 전체를 [distill-rubric.md](references/distill-rubric.md) 4분류로. 누적 판정이므로 **교차 repo 패턴**을 별도 섹션으로 올릴 수 있다. `이미 있음` 주장에는 **스킬 이름 명시** — 못 대면 `이미 있음`이 아니다.
3. **배달** — Slack DM + Obsidian `Inbox/release-digest-<YYYY-MM-DD>.md`.
4. **드레인** — 배달이 끝난 뒤에만 `python3 assets/watch.py digest --drain`. 판정·배달이 죽으면 큐를 남긴다 — 다음 digest가 다시 잡는다.
5. **receipt** — 첫 줄에 `stage: digest (큐 N건 판정)`. 이어서 Outcome / Evidence(판정 수·분류 분포) / Artifact / Next Action.

## Example

`poll` → `new: [{repo: stablyai/orca, id: v1.4.196, highlights: [...]}]` → watch가 "orca v1.4.196 — 부모 워크트리 선택 외 N건" DM (판정 없음). 며칠 뒤 digest가 큐 9건을 한꺼번에 판정. `new: [], quiet: true, needs_attention: false`면 **watch Step 2에서 종료** — LLM도 DM도 없다.

## 판정에 영향 주는 것

watchlist·watermark·필터·큐 파일은 전부 `watch.py`가 소유한다 (LLM 0). 판정에 걸리는 건 둘뿐:

- **억제된 릴리즈는 알림과 큐 양쪽에서 빠진다** — digest는 "알린 것 중에서" 판정한다. `@minor`/`@major` 임계와 prerelease 제외가 여기 걸린다.
- **highlights가 빌 수 있다** — 산문 본문이거나 전부 필터에 걸린 경우. 알림은 이름 + 링크로 폴백한다.

watchlist 표기(`owner/repo`, 경로 모드 `owner/repo:dir`), 필터 규칙, 파일 3종의 소유·씨딩·등록은 [config.md](references/config.md).

## Error Handling

- watchlist 없음 → `empty_watchlist`. `watch.py seed`로 후보를 제시하고 사람이 솎는다.
- `gh` 미인증 → `failed[]`. `gh auth login --hostname github.com` 안내. state 무변경이라 복구 후 놓친 릴리즈가 그대로 잡힌다.
- Slack 실패 → Obsidian은 계속, `→ ESCALATE: Slack 전송 실패`. Obsidian 실패 → 터미널 fallback. 어느 쪽이든 digest였다면 드레인하지 않는다.
- 큐 파일 손상 → 백로그만 잃고 폴링은 계속된다.
