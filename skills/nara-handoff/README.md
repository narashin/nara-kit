# nara-handoff: 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Record where this session stopped — in-progress threads, open questions, verification state, next safe step — into docs/handoff.md by merging with the previous handoff, so the next session's nara-now resumes without re-deriving context.

## 호출

- Claude Code: `/nara-handoff`
- Codex: `$nara-handoff`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "handoff", "인계", "여기까지 남겨", "이어서 할 수 있게", "세션 끊기 전에", "다음 세션용 메모", "세션 마무리" when work is unfinished.
- **DO NOT USE FOR:** 배운 것·실수에서 재발 방지 찾기 (→ nara-retro), 다음 할 일 추천 (→ nara-now), 결정 기록 (→ nara-adr), 메모리 정리 (→ nara-grooming).

## 이웃 스킬과의 차이

nara-handoff는 "어디서 멈췄나"만 남긴다. 배운 것과 재발 방지는 nara-retro가 맡고, 다음 세션에서 이 파일을 읽어 다음 행동을 추천하는 것은 nara-now다.

## 설계 메모

예전 nara-reflect의 handoff 부분을 떼어 낸 스킬이다. 9절 스키마, carry-forward merge, 비면 삭제하는 규칙은 그대로다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
