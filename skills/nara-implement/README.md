# nara-implement — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Implement an approved code change under a verification gate, then stop at staged — never auto-commit. Supports a TDD option (red→green) and direct/delegated execution. Verdict: Pass | Fail | Blocked | Unverifiable.

## 호출

- Claude Code: `/nara-implement`
- Codex: `$nara-implement`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "구현", "implement", "execute", "이 계획대로 짜줘", "작업 단위 구현", dev-mode execute step.
- **DO NOT USE FOR:** 테스트 코드만 생성 (→ nara-test-implement), 장애 수정 (→ nara-incident-fix), 커밋 메시지 (→ nara-commit), 원인 불명 버그 (→ nara-incident).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
