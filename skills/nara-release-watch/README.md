# nara-release-watch — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

구독 중인 GitHub repo를 두 단계로 감시한다. **watch**(매일, autopilot)는 새 릴리즈를 판정 없이 알리고 큐에 쌓는다. **digest**(사람 트리거)는 쌓인 큐를 한꺼번에 놓고 nara-kit에 증류할 값이 있는지 판정한다.

## 호출

- watch (기본): `/nara-release-watch` (`--dry-run` 가능) · Codex `$nara-release-watch`
- digest: `/nara-release-watch digest`
- 폴링만: `python3 skills/nara-release-watch/assets/watch.py poll --limit 5`
- 큐 확인: `... watch.py digest` (읽기만 — `--drain`은 배달 완료 후)
- 목록 확인: `... watch.py list` · 후보 씨딩: `... watch.py seed --top 50`

목록은 `~/.claude/release-watch.md`에서 직접 편집한다. 형식·등록 절차는 [references/config.md](references/config.md).

## 언제 쓰나

- **USE FOR:** "release watch", "watchlist 확인", "새 릴리즈", "릴리즈 감시", "release digest", "증류할 거 있나".
- **DO NOT USE FOR:** 모르는 repo 발견 (→ nara-trending-digest), 특정 repo 검색 (→ WebSearch), 라이브러리 문서 (→ Context7), 스킬 개선 실행 (→ nara-skill-forge).

`nara-trending-digest`와 짝이지만 다른 일이다 — trending은 **모르는 repo 발견**, 이건 **아는 repo 추적**. 배달 경로(Slack DM + Obsidian)만 공유한다.

## 왜 알림과 판정을 갈랐나

판정을 릴리즈 단위로 매일 하면 릴리즈 잦은 repo는 감시가 불가능하다. stablyai/orca는 minor가 오래 고정된 채 하루 한 번 패치를 낸다 — `@minor` 임계를 붙이면 알림까지 영원히 죽고, 안 붙이면 매일 발화한다. 임계가 알림과 판정을 동시에 죽이는 게 문제였으므로 둘을 갈랐다:

- **watch**는 매일 돌지만 LLM 판정이 없다. 기계 필터(fix/chore prefix, "Notable changes" 마케팅 섹션 제거)를 통과한 기능성 변경 줄만 "새로 나왔대"로 전달한다.
- **digest**는 사람이 트리거하고, 큐 누적분(대개 1주, 여러 repo)을 한꺼번에 판정한다. 누적이라 **교차 repo 패턴**(여러 repo가 같은 방향으로 움직인 것)이 보인다 — 릴리즈 단위 판정으로는 절대 안 보이는 것.

jira-triage(자동 큐 적재) → jira-drain(사람 트리거)과 같은 구조라 잡은 계속 1개다.

## 왜 조용한 날엔 아무것도 안 보내나

AI 툴링 repo 릴리즈는 버스티하다. 매일 확인해서 매일 보고하면 6일은 "없음"이고, 그러면 진짜 있는 7일째도 안 읽는다. 그래서 **폴링은 매일, 알림은 있을 때만**이다.

예외는 `needs_attention`이다. `gh` 인증이 깨지면 조용한 날과 구별할 수 없으므로, 실패는 조용함으로 접지 않고 매 실행 보고한다.

## 노이즈 통제

실제로 붙여보니 터진 곳들이다.

| repo | 문제 | 대응 |
|---|---|---|
| `openai/codex` | 알파를 플래그 없이 정식 릴리즈로 올림 | prerelease 기본 제외, 태그 문자열로도 판정 |
| `anthropics/claude-code` | 패치 릴리즈가 거의 매일 | watchlist에 `@minor` 표시 |
| `stablyai/orca` | 주간 PR 불릿 617줄 중 8할이 fix() | highlights 기계 필터 (LLM 0) |

억제된 릴리즈도 `last_seen`은 전진하고, 큐에는 들어가지 않는다 — digest는 "알린 것 중에서" 판정한다.

## 판정이 digest의 산출물이다

watch 알림은 요약이고, digest 산출물은 4분류 판정이다. **기본값은 `의존`** — 이 잡은 구조상 흡수 루프라서 기본값이 `증류 후보`면 "우리도 만들자" 후보만 쌓인다. `이미 있음` 판정에는 **스킬 이름을 반드시 대야 한다.** 루브릭은 [references/distill-rubric.md](references/distill-rubric.md).

## 설계 메모

폴링·필터·상태·큐는 `assets/watch.py`(표준 라이브러리 + `gh` CLI)가 소유한다. 테스트는 `assets/test_watch.py` — `python3 -m pytest skills/nara-release-watch/assets/test_watch.py -q`. GitHub 호출은 주입 가능해서 테스트가 네트워크를 타지 않는다. digest의 읽기와 드레인이 분리된 이유: 판정·배달이 죽어도 백로그를 잃지 않기 위해서다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
