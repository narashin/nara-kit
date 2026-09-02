# nara-release-watch — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

구독 중인 GitHub repo의 새 릴리즈를 매일 확인하고, nara-kit에 증류할 값이 있는 것만 골라 알린다.

## 호출

- Claude Code: `/nara-release-watch` (`--dry-run` 가능)
- Codex: `$nara-release-watch`
- 폴링만: `python3 skills/nara-release-watch/assets/watch.py poll --limit 5`
- 목록 확인: `... watch.py list`
- 후보 씨딩: `... watch.py seed --top 50`

목록은 `~/.claude/release-watch.md`에서 직접 편집한다. 형식·등록 절차는 [references/config.md](references/config.md).

## 언제 쓰나

- **USE FOR:** "release watch", "watchlist 확인", "구독 repo 새 릴리즈", "증류할 거 있나", "릴리즈 감시".
- **DO NOT USE FOR:** 모르는 repo 발견 (→ nara-trending-digest), 특정 repo 검색 (→ WebSearch), 라이브러리 문서 (→ Context7), 스킬 개선 실행 (→ nara-skill-forge).

`nara-trending-digest`와 짝이지만 다른 일이다 — trending은 **모르는 repo 발견**, 이건 **아는 repo 추적**. 배달 경로(Slack DM + Obsidian)만 공유한다.

## 왜 두 층인가

"새 릴리즈 있나"는 GitHub API 한 방이다 (LLM 0). "이게 증류할 만한가"는 nara-kit 스킬 표면을 알아야 하는 판단이다.

두 층을 분리하면 **신규 0건인 날에 모델을 아예 안 깨운다.** 기존 autopilot이 Claude 풀을 절반쯤 쓰고 있으니 이건 실질적인 절약이다.

## 왜 조용한 날엔 아무것도 안 보내나

AI 툴링 repo 릴리즈는 버스티하다. 매일 확인해서 매일 보고하면 6일은 "없음"이고, 그러면 진짜 있는 7일째도 안 읽는다. 그래서 **폴링은 매일, 알림은 있을 때만**이다.

매일 도는데 대개 산출물이 없는 것이 정상 동작이다.

예외는 `needs_attention`이다. `gh` 인증이 깨지면 조용한 날과 구별할 수 없으므로, 실패는 조용함으로 접지 않고 매 실행 보고한다. 이게 없으면 토큰이 만료된 뒤 영구히 "평온한" 상태로 보인다.

## 노이즈 통제

실제로 붙여보니 두 군데가 터졌다.

| repo | 문제 | 대응 |
|---|---|---|
| `openai/codex` | 최신이 `rust-v0.153.0-alpha.5` — 알파를 플래그 없이 정식 릴리즈로 올림 | prerelease 기본 제외, 태그 문자열로도 판정 |
| `anthropics/claude-code` | `v2.1.258` — 패치 릴리즈가 거의 매일 | watchlist에 `@minor` 표시 |

억제된 릴리즈도 `last_seen`은 전진한다. 안 그러면 같은 패치를 매 실행 재평가하고 영원히 수렴하지 않는다.

## 판정이 산출물이다

릴리즈노트 요약은 링크가 더 잘한다. 값이 있는 건 4분류 판정이고, **기본값은 `의존`**이다 — 이 잡은 구조상 흡수 루프라서 기본값이 `증류 후보`면 매일 "우리도 만들자" 후보만 쌓인다. 루브릭은 [references/distill-rubric.md](references/distill-rubric.md).

`이미 있음` 판정에는 **스킬 이름을 반드시 대야 한다.** 이름을 못 대면 그건 인상이고, 인상으로 릴리즈를 버리면 진짜 새로운 것을 놓친다.

## 설계 메모

폴링·필터·상태는 `assets/watch.py`(표준 라이브러리 + `gh` CLI)가 소유한다. 테스트는 `assets/test_watch.py` — `python3 -m pytest skills/nara-release-watch/assets/test_watch.py -q`. GitHub 호출은 주입 가능해서 테스트가 네트워크를 타지 않는다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
