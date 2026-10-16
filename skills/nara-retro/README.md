# nara-retro: 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Look back at how a session went or why a skill misbehaved: tie each lesson to observed evidence, separate confirmed causes from guesses, and route the smallest prevention to its owner — write memory directly (with preview), recommend a test/lint/script, CLAUDE.md rule, skill fix, hook or ADR, or conclude no change. A nara-kit skill failure becomes a redacted improvement proposal.

## 호출

- Claude Code: `/nara-retro`
- Codex: `$nara-retro`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "retro", "회고", "세션 회고", "오늘 배운 것", "이거 어디 저장", "왜 또 틀렸지", "재발 방지", "이 스킬 불편했어", "nara-kit 개선 피드백", "스킬로 만들까", "결정 기록할 거 있나".
- **DO NOT USE FOR:** 하다 만 일·열린 질문 인계 (→ nara-handoff), 기존 규칙·메모리 중복·충돌 감사 (→ nara-grooming), 스킬 개선 실행 (→ nara-skill-forge), 코드 리뷰 (→ nara-code-review), 아키텍처 결정 문서 작성 (→ nara-adr).

## 이웃 스킬과의 차이

nara-retro는 "무엇을 배웠고 무엇을 바꿔야 하나"를 다룬다. 하다 만 일은 nara-handoff, 이미 있는 규칙·메모리의 중복과 충돌은 nara-grooming, 제안한 스킬 수정의 실행은 nara-skill-forge가 맡는다.

## 설계 메모

예전 nara-reflect의 학습 라우팅과 nara-meta-feedback의 redacted 개선안을 합쳤다. MTGVim/tiger-kit `tk-retro`(`5e633e3`, MIT)에서 증거 사슬(관찰, 영향, 원인 확신도, 최소 예방, 소유 층, 판정 검사), 결정적 검사 우선, `no change`를 정상 결론으로 보는 원칙, 실패 평면과 사건·대조군 재현을 가져왔다. `tk-compound`에서는 리뷰 지적을 확정·기각·미해결로 가르고 독립 사건 수로 세는 규칙만 가져왔다. tiger-kit 공통 블록(결과 요약 서식, 질문 라운드, 산출물 경로)은 가져오지 않았다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
